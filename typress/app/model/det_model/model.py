import onnxruntime
from pathlib import Path
import os
import requests
from tqdm import tqdm
from .infer import PredictConfig


def download_file(url, destination):
    response = requests.get(url, stream=True)
    
    if response.status_code == 200:
        total_size = int(response.headers.get('content-length', 0))

        with open(destination, 'wb') as f, tqdm(
                total=total_size, unit='B', unit_scale=True) as bar:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    bar.update(len(chunk))
    else:
        print(f"Download failed: {response.status_code}")


def download_det_model():
    filename = Path(__file__).resolve().parent
    filename = filename.parent.parent.parent.parent / ".cache" / "rtdetr_r50vd_6x_coco.onnx"
    url = "https://huggingface.co/TonyLee1256/texteller_det/resolve/main/rtdetr_r50vd_6x_coco.onnx?download=true"
    if(not os.path.exists(filename)):
        if(not os.path.exists(filename.parent)):
            os.mkdir(filename.parent)
        download_file(url, filename)

    return str(filename)


def load_det_model(device):
    model_path = download_det_model()

    predictor = None
    if device.type == "cuda":
        options = onnxruntime.SessionOptions()
        options.enable_cpu_mem_arena = False

        cuda_provider = ("CUDAExecutionProvider", {
            "device_id": device.index,        
            "arena_extend_strategy": "kNextPowerOfTwo",      
            "gpu_mem_limit": 3 * 1024 * 1024 * 1024,    
            "cudnn_conv_algo_search": "EXHAUSTIVE",
            "do_copy_in_default_stream": True,
        })

        predictor = onnxruntime.InferenceSession(model_path,
                                                sess_options=options,
                                                providers=[cuda_provider])

    else:
        predictor = onnxruntime.InferenceSession(model_path, providers=['CPUExecutionProvider'])

    cfg_path = Path(__file__).resolve()
    cfg_path = cfg_path.parent / "config" / "infer_cfg.yml"

    infer_config = PredictConfig(str(cfg_path))
    return predictor, infer_config
