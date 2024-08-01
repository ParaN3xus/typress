from torch.utils.data import Dataset
from PIL import Image
import torch
from torch.utils.data import DataLoader
import pandas
import os


class OCRDataset(Dataset):
    def __init__(self, root_dir, df, processor, max_target_length=512):
        self.root_dir = root_dir
        self.df = df
        self.processor = processor
        self.max_target_length = max_target_length

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        # get file name + text
        file_name = self.df["file_name"][idx]
        text = self.df["text"][idx]

        # prepare image (i.e. resize + normalize)
        image = Image.open(self.root_dir + file_name).convert("RGB")
        pixel_values = self.processor(image, return_tensors="pt").pixel_values

        # add labels (input_ids) by encoding the text
        labels = self.processor.tokenizer(
            text,
            padding="max_length",
            max_length=self.max_target_length,
            truncation=True,
        ).input_ids

        # important: make sure that PAD tokens are ignored by the loss function
        labels = [
            label if label != self.processor.tokenizer.pad_token_id else -100
            for label in labels
        ]

        encoding = {
            "pixel_values": pixel_values.squeeze(),
            "labels": torch.tensor(labels),
        }
        return encoding


def get_dataset_df(csv_path):
    df = pandas.read_csv(f"{csv_path}", header=None)
    df.rename(columns={0: "file_name", 1: "text"}, inplace=True)
    df = df.drop(index=0)
    df["text"] = df["text"].astype(str)
    return df.reset_index(drop=True)


def get_dataloader(csv_path, batch_size, num_workers, processor):
    df = get_dataset_df(csv_path)
    dataset = OCRDataset(
        root_dir=f"{os.path.dirname(csv_path)}/img/", df=df, processor=processor
    )
    return DataLoader(dataset, batch_size=batch_size, num_workers=num_workers, shuffle=True)
