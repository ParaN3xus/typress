from .ocr_model.model import load_ocr_model, generate
from .det_model.model import load_det_model
from .det_model.infer import predict as det_infer
from .utils import get_device
from PIL import Image
import gc
import numpy as np

def crop_bbox(img, bbox: dict):
    crop_area = (bbox["x"], bbox["y"], bbox["x"] + bbox["width"], bbox["y"] + bbox["height"])

    cropped_img = img.crop(crop_area)
    
    return cropped_img


def in_rate(bbox1, bbox2):
    x1, y1, w1, h1 = bbox1["x"], bbox1["y"], bbox1["width"], bbox1["height"]
    x2, y2, w2, h2 = bbox2["x"], bbox2["y"], bbox2["width"], bbox2["height"]

    x_int1 = max(x1, x2)
    y_int1 = max(y1, y2)
    x_int2 = min(x1 + w1, x2 + w2)
    y_int2 = min(y1 + h1, y2 + h2)

    intersection_width = max(0, x_int2 - x_int1)
    intersection_height = max(0, y_int2 - y_int1)
    intersection_area = intersection_width * intersection_height

    area1 = w1 * h1

    iou = intersection_area / area1 if area1 != 0 else 1
    return iou


class typressmodel:
    def __init__(
        self,
        det_model = None,
        ocr_model = "paran3xus/typress_ocr",
        device = "auto"
    ):
        self.device = get_device(device)

        self.det_model, self.det_config = load_det_model(self.device)
        self.ocr_model, self.processor = load_ocr_model(ocr_model, self.device)
        

    def detect(self, img):
        img_data = np.frombuffer(img.read(), dtype=np.uint8)
        bbox = det_infer(img_data, self.det_model, self.det_config)
        
        bbox = [{
            "x": b.p.x,
            "y": b.p.y,
            "width": b.w,
            "height": b.h
        } for b in bbox]
        
        filtered_bbox = []
        for i, box1 in enumerate(bbox):
            keep = True
            for j, box2 in enumerate(bbox):
                if i != j: 
                    iou = in_rate(box1, box2)
                    if iou > 0.9:
                        keep = False
                        break
            if keep:
                filtered_bbox.append(box1)
        
        return filtered_bbox


    def recognize(self, img, bbox):
        img = Image.open(img).convert("RGB")

        cropped_img = crop_bbox(img, bbox)
        pixel_values = self.processor(images=cropped_img, return_tensors="pt").pixel_values.to(
            self.device
        )
        text = generate(self.ocr_model, self.processor, pixel_values)[0]

        return text