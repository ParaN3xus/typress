from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image


def generate(model, processor, pixel_values):
    generated_ids = model.generate(pixel_values)
    generated_texts = processor.batch_decode(
        generated_ids, skip_special_tokens=True)
    return generated_texts


def generate_cli(model_path, image_path, continuous):
    model, processor = load_model(model_path)

    while True:
        if continuous:
            image_path = input("Input image file path: ")

        image_fps = [image_path]
        images = [Image.open(fp).convert("RGB") for fp in image_fps]
        pixel_values = processor(
            images=images, return_tensors="pt").pixel_values
        generated_text = generate(model, processor, pixel_values)
        [print(i) for i in generated_text]

        if not continuous:
            break


def load_model(path):
    processor = TrOCRProcessor.from_pretrained(path)
    model = VisionEncoderDecoderModel.from_pretrained(path)
    return model, processor


def save_model(path, model, processor):
    model.save_pretrained(path)
    processor.save_pretrained(path)
