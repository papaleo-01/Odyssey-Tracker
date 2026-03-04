from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

APP_PASSWORD = os.getenv("APP_PASSWORD", "changeme")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "0.0.0.0")
CURRENCY = os.getenv("CURRENCY", "€")
APP_TITLE = os.getenv("APP_TITLE", "Car Cost Tracker")
DB_PATH = BASE_DIR / "data" / "car_tracker.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"
