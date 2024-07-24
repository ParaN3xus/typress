from dotenv import load_dotenv
import os
from typress.app.api import get_app

load_dotenv()

model_path = os.getenv("MODEL_PATH")
api_root = os.getenv("API_ROOT_URL")

app = get_app(
    model_path=model_path,
    device="auto",
    api_root=api_root
)
