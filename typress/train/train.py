from tqdm import tqdm
import torch
import json
from datetime import datetime
from .eval import eval
from .dataset import get_dataloader
from ..app.model.ocr_model.model import save_model, load_ocr_model
from torch.utils.data import DataLoader


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


def train(model, train_dataloader, optimizer, device, logger: Logger, log_step):
    model.train()
    train_loss = 0.0
    batch_count = 0

    prog = tqdm(train_dataloader)
    for batch in prog:
        # get the inputs
        for k, v in batch.items():
            batch[k] = v.to(device)

        # forward + backward + optimize
        outputs = model(**batch)
        loss = outputs.loss
        loss = loss.mean()
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        train_loss += loss.item()
        batch_count += 1

        if batch_count % log_step == 0:
            metrics = {
                "step": batch_count,
                "loss": loss.item(),
                "avg_loss": train_loss / batch_count,
                "learning_rate": optimizer.param_groups[0]['lr']
            }
            logger.log_metrics(metrics)

        prog.set_description(desc=f"loss: {loss.item()}")

    return train_loss


def train_and_eval(
    model,
    processor,
    train_dataloader: DataLoader,
    eval_dataloader: DataLoader,
    epoches,
    learning_rate,
    eval_step,
    save_path,
    device,
    logger: Logger,
    log_step,
):
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
    model = torch.nn.DataParallel(model)

    for epoch in range(epoches):
        logger.log_metrics({"epoch": epoch, "status": "started"})

        train_loss = train(model, train_dataloader,
                           optimizer, device, logger, log_step)

        save_model(f"{save_path}/epoch_{epoch}/", model.module, processor)

        epoch_metrics = {
            "epoch": epoch,
            "status": "completed",
            "train_loss": train_loss / len(train_dataloader),
            "valid_cer": "didn't eval"
        }

        if ((epoch + 1) % eval_step == 0):
            epoch_metrics["valid_cer"] = eval(
                model, eval_dataloader, device, logger)

        logger.log_metrics(epoch_metrics)


def cli_train(config_path):
    import json

    with open(config_path, "r") as f:
        config = json.load(f)

    model_path = config["model"]
    train_data_path = config["dataset"]["train"]
    eval_data_path = config["dataset"]["eval"]
    epoches = config["params"]["epoches"]
    learning_rate = config["params"]["learning_rate"]
    freeze_encoder = config["params"]["freeze_encoder"]
    train_batch_size = config["params"]["train_batch_size"]
    eval_batch_size = config["params"]["eval_batch_size"]
    eval_step = config["params"]["eval_step"]
    dataloader_num_workers = config["params"]["dataloader_num_workers"]
    save_path = config["model"]
    log_file = config["logging"]["path"]
    log_step = config["logging"]["log_step"]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    logger = Logger(log_file)
    try:
        logger.log_config(config)

        model, processor = load_ocr_model(model_path, device)

        if freeze_encoder:
            for param in model.encoder.parameters():
                param.requires_grad = False

        train_dataloader: DataLoader = get_dataloader(
            train_data_path, train_batch_size, dataloader_num_workers, processor)
        eval_dataloader: DataLoader = get_dataloader(
            eval_data_path, eval_batch_size, dataloader_num_workers, processor)

        train_and_eval(
            model,
            processor,
            train_dataloader,
            eval_dataloader,
            epoches,
            learning_rate,
            eval_step,
            save_path,
            device,
            logger,
            log_step,
        )
    finally:
        logger.close()
