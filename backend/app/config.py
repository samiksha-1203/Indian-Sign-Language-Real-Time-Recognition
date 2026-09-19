"""
config.py
=========
Centralized configuration. Reads from environment variables where sensible,
falls back to sane defaults.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/

MODELS_DIR = Path(os.getenv("ISL_MODELS_DIR", BASE_DIR / "models"))
DEFAULT_DATASET_DIR = BASE_DIR / "datasets" / "ISL"
WORKSPACE_DATASET_DIR = BASE_DIR.parent / "Indian"
DATASET_DIR = Path(os.getenv(
	"ISL_DATASET_DIR",
	DEFAULT_DATASET_DIR if DEFAULT_DATASET_DIR.exists() else WORKSPACE_DATASET_DIR,
))
DATASET_REPORT_PATH = Path(os.getenv("ISL_DATASET_REPORT", BASE_DIR / "datasets" / "dataset_report.json"))

DATABASE_PATH = Path(os.getenv("ISL_DB_PATH", BASE_DIR / "signspeak.db"))
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Inference / smoothing defaults - overridable via the API where noted.
CONFIDENCE_THRESHOLD_DEFAULT = float(os.getenv("ISL_CONFIDENCE_THRESHOLD", 0.85))
SMOOTHING_WINDOW_SIZE = int(os.getenv("ISL_SMOOTHING_WINDOW", 7))
SMOOTHING_MIN_STABLE = int(os.getenv("ISL_SMOOTHING_MIN_STABLE", 5))
SMOOTHING_COOLDOWN_SEC = float(os.getenv("ISL_SMOOTHING_COOLDOWN_SEC", 1.0))

CORS_ORIGINS = os.getenv("ISL_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
