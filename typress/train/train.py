from typing import List
from tqdm import tqdm
import torch
import json
from datetime import datetime
from .eval import eval
from .dataset import get_dataloader
from ..app.model.ocr_model.model import save_model, load_ocr_model
from torch.utils.data import DataLoader
from torch.nn.parallel import DistributedDataParallel
from torch.nn import DataParallel
import os
import torch.distributed as dist
import math
from torch.optim.lr_scheduler import LambdaLR

class Logger:
    def __init__(self, log_file):
        self.f = open(log_file, 'a')

    def log_config(self, config):
        self.f.write(f"=== Training started at {datetime.now()} ===\n")
        self.f.write("Configuration:\n")
        self.f.write(json.dumps(config, indent=2))
        self.f.write("\n\n")
        self.f.flush()

    def log_metrics(self, metrics):
        self.f.write(f"[{datetime.now()}] {json.dumps(metrics)}\n")
        self.f.flush()

    def close(self):
        self.f.close()

class NoScheduler:
    def __init__(self):
        pass

    def step(self):
        pass 


def inner_model(model):
    match model:
        case DataParallel() | DistributedDataParallel():
            return model.module
        case _ :
            return model

def get_linear_warmup_cosine_lr_scheduler(
    optimizer,
    num_training_steps,
    warmup_steps,
    init_lr,
    min_lr,
    warmup_lr
):
    def lr_lambda(current_step):
        if current_step < warmup_steps:
            return warmup_lr + (init_lr - warmup_lr) * current_step / warmup_steps
        
        progress = float(current_step - warmup_steps) / float(max(1, num_training_steps - warmup_steps))
        return max(min_lr, min_lr + (init_lr - min_lr) * 0.5 * (1.0 + math.cos(math.pi * progress)))
    
    return LambdaLR(optimizer, lr_lambda)

def train(model, train_dataloader, optimizer, lr_scheduler, device, logger: Logger, log_step, epoch):
    model.train()
    train_loss = 0.0
    batch_count = 0

    if hasattr(train_dataloader.sampler, 'set_epoch'):
        train_dataloader.sampler.set_epoch(epoch)

    ddp_flag = isinstance(model, DistributedDataParallel)
    master_flag = True
    if(ddp_flag):
        master_flag = dist.get_rank() == 0

    if master_flag:
        prog = tqdm(train_dataloader)
    else:
        prog = train_dataloader

    for batch in prog:
        # get the inputs
        for k, v in batch.items():
            batch[k] = v.to(device)

        # forward + backward + optimize
        outputs = model(**batch)
        loss = outputs.loss
        if not ddp_flag:
            loss = loss.mean()
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        lr_scheduler.step()

        train_loss += loss.item()
        batch_count += 1

        if master_flag:
            if batch_count % log_step == 0:
                metrics = {
                    "step": batch_count,
                    "loss": loss.item(),
                    "avg_loss": train_loss / batch_count,
                    "learning_rate": optimizer.param_groups[0]['lr']
                }
                logger.log_metrics(metrics)

            if isinstance(prog, tqdm):
                prog.set_description(desc=f"loss: {loss.item()}")


    train_loss = torch.tensor(train_loss).to(device)
    return train_loss


def train_and_eval(
    model,
    processor,
    train_dataloader: DataLoader,
    eval_dataloaders: List[DataLoader],
    epoches,
    scheduler_conf,
    eval_step,
    save_path,
    device,
    logger: Logger,
    log_step,
):
    match scheduler_conf["mode"]:
        case "const_lr":
            optimizer = torch.optim.AdamW(model.parameters(), lr=scheduler_conf["lr"])

            lr_scheduler = NoScheduler()
        case "linear_warmup_cosine_lr":
            optimizer = torch.optim.AdamW(
                model.parameters(),
                lr=scheduler_conf["init_lr"],
                weight_decay=scheduler_conf["weight_decay"]
            )
            
            num_training_steps = len(train_dataloader) * epoches
            
            lr_scheduler = get_linear_warmup_cosine_lr_scheduler(
                optimizer,
                num_training_steps,
                scheduler_conf["warmup_steps"],
                scheduler_conf["init_lr"],
                scheduler_conf["min_lr"],
                scheduler_conf["warmup_lr"]
            )


    ddp_flag = isinstance(model, DistributedDataParallel)
    master_flag = True
    if(ddp_flag):
        master_flag = dist.get_rank() == 0

    for epoch in range(epoches):
        if master_flag:
            logger.log_metrics({"epoch": epoch, "status": "started"})

        train_loss = train(model, train_dataloader,
                           optimizer, lr_scheduler, device, logger, log_step, epoch)

        if ddp_flag:
            dist.all_reduce(train_loss, op=dist.ReduceOp.SUM)
            train_loss = train_loss / dist.get_world_size()

        if master_flag:
            save_model(f"{save_path}/epoch_{epoch}/",
                    inner_model(model), processor)

            epoch_metrics = {
                "epoch": epoch,
                "status": "completed",
                "train_loss": train_loss.item() / len(train_dataloader),
                "valid_cer": "didn't eval"
            }

            if ((epoch + 1) % eval_step == 0):
                epoch_metrics["valid_cer"] = eval(
                    model, eval_dataloaders, device, logger)

            logger.log_metrics(epoch_metrics)


def cli_train(config_path):
    import json

    with open(config_path, "r") as f:
        config = json.load(f)

    model_path = config["model"]
    train_data_path = config["dataset"]["train"]
    eval_data_path = config["dataset"]["eval"]
    epoches = config["params"]["epoches"]
    scheduler = config["params"]["scheduler"]
    freeze_encoder = config["params"]["freeze_encoder"]
    train_batch_size = config["params"]["train_batch_size"]
    eval_batch_size = config["params"]["eval_batch_size"]
    eval_step = config["params"]["eval_step"]
    dataloader_num_workers = config["params"]["dataloader_num_workers"]
    save_path = os.path.join(config["model"], f"{datetime.now()}")
    log_file = config["logging"]["path"]
    log_step = config["logging"]["log_step"]
    dist_mode = config["dist"]["mode"]

    logger = Logger(log_file)
    try:
        logger.log_config(config)

        match dist_mode:
            case None | "dp":
                device = torch.device(f"cuda" if torch.cuda.is_available() else "cpu")
            case "ddp":
                local_rank = int(os.environ["LOCAL_RANK"])
                torch.cuda.set_device(local_rank)
                dist.init_process_group(backend="nccl")
                dist.barrier()
                device = torch.device(f"cuda:{local_rank}" if torch.cuda.is_available() else "cpu")
            case _:
                raise Exception("Invalid distribute mode")

        model, processor = load_ocr_model(model_path, device)

        if freeze_encoder:
            for param in model.encoder.parameters():
                param.requires_grad = False

        match dist_mode:
            case "dp":
                model = DataParallel(model)
            case "ddp":
                model = DistributedDataParallel(model,
                                     device_ids=[local_rank],
                                     find_unused_parameters=True)
            case _:
                pass

        train_dataloader: DataLoader = get_dataloader(
            train_data_path, train_batch_size, dataloader_num_workers, processor, True, dist_mode)
        eval_dataloaders: List[DataLoader] = [get_dataloader(
            path, eval_batch_size, dataloader_num_workers, processor, False, dist_mode) for path in eval_data_path]

        train_and_eval(
            model,
            processor,
            train_dataloader,
            eval_dataloaders,
            epoches,
            scheduler,
            eval_step,
            save_path,
            device,
            logger,
            log_step,
        )
    except KeyboardInterrupt:
        save_model(f"{save_path}/interrupted/",
            inner_model(model), processor)
    finally:
        if dist_mode == "ddp":
            dist.destroy_process_group()
        logger.close()
