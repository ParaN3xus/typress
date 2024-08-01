from tqdm import tqdm
import torch
from .eval import eval
from .dataset import get_dataloader
from ..app.model import save_model, load_model


def train(model, train_dataloader, optimizer, device):
    model.train()
    train_loss = 0.0

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

        prog.set_description(desc=f"loss: {loss.item()}")

    return train_loss


def train_and_eval(
    model,
    processor,
    train_dataloader,
    eval_dataloader,
    epoches,
    learning_rate,
    save_path,
    device,
):
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
    model = torch.nn.DataParallel(model)

    for epoch in range(epoches):
        train_loss = train(model, train_dataloader, optimizer, device)
        valid_cer = eval(model, processor, eval_dataloader, device)

        save_model(f"{save_path}/epoch_{epoch}/", model.module, processor)

        print(f"Loss after epoch {epoch}:", train_loss / len(train_dataloader))
        print("Validation CER:", valid_cer / len(eval_dataloader))
        print("Model saved")


def cli_train(config_path):
    import json

    with open(config_path, "r") as f:
        config = json.load(f)

    model_path = config["model"]
    train_data_path = config["dataset"]["train"]
    eval_data_path = config["dataset"]["eval"]
    epoches = config["params"]["epoches"]
    learning_rate = config["params"]["learning_rate"]
    train_batch_size = config["params"]["train_batch_size"]
    eval_batch_size = config["params"]["eval_batch_size"]
    dataloader_num_workers = config["params"]["dataloader_num_workers"]
    save_path = config["model"]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model, processor = load_model(model_path, device)

    train_dataloader = get_dataloader(train_data_path, train_batch_size, dataloader_num_workers, processor)
    eval_dataloader = get_dataloader(eval_data_path, eval_batch_size, dataloader_num_workers, processor)

    train_and_eval(
        model,
        processor,
        train_dataloader,
        eval_dataloader,
        epoches,
        learning_rate,
        save_path,
        device,
    )
