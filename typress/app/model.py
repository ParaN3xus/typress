from typing import Tuple
from transformers import PreTrainedModel, TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image


def get_device(device_name):
    import torch

    device = None
    if device_name == "auto":
        if torch.cuda.is_available():
            device = torch.device("cuda:0")
        elif torch.backends.mps.is_available():
            device = torch.device("mps")
        else:
            device = torch.device("cpu")
    else:
        device = torch.device(device_name)

    return device


def generate(model, processor, pixel_values):
    generated_ids = model.generate(pixel_values.to(next(model.parameters()).device))
    generated_texts = processor.batch_decode(generated_ids, skip_special_tokens=True)
    return generated_texts


def generate_cli(model_path, image_path, continuous, device_name):

    device = get_device(device_name)
    model, processor = load_model(model_path, device)

    while True:
        if continuous:
            image_path = input("Input image file path: ")

        img = Image.open(image_path).convert("RGB")
        pixel_values = processor(images=img, return_tensors="pt").pixel_values
        generated_text = generate(model, processor, pixel_values)
        print(generated_text)

        if not continuous:
            break


def load_model(path, device) -> Tuple[PreTrainedModel, TrOCRProcessor]:
    model = VisionEncoderDecoderModel.from_pretrained(path)
    processor = TrOCRProcessor.from_pretrained(path)
    assert isinstance(processor, TrOCRProcessor)
    return model.to(device), processor


def save_model(path, model, processor):
    model.save_pretrained(path)
    processor.save_pretrained(path)
