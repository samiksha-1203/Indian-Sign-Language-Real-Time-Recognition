"""
analytics.py (service)
=======================
All numbers here come from either the SQLite prediction_history table or
the real JSON reports written by dataset_inspector.py / evaluate.py -
nothing is invented.
"""

import json
from collections import Counter
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import DATASET_REPORT_PATH, MODELS_DIR
from app.database import PredictionHistory


def log_prediction(db: Session, session_id: str, predicted_class: str, confidence: float):
    entry = PredictionHistory(
        session_id=session_id, predicted_class=predicted_class, confidence=confidence
    )
    db.add(entry)
    db.commit()


def get_summary(db: Session, limit_recent: int = 10):
    rows = db.query(PredictionHistory).all()
    total = len(rows)
    if total == 0:
        return {
            "total_predictions": 0,
            "average_confidence": 0.0,
            "most_recognized_character": None,
            "recent_predictions": [],
        }

    avg_conf = sum(r.confidence for r in rows) / total
    counts = Counter(r.predicted_class for r in rows)
    most_common = counts.most_common(1)[0][0]

    recent = sorted(rows, key=lambda r: r.timestamp, reverse=True)[:limit_recent]
    recent_list = [
        {
            "predicted_class": r.predicted_class,
            "confidence": r.confidence,
            "timestamp": r.timestamp.isoformat() if r.timestamp else None,
            "session_id": r.session_id,
        }
        for r in recent
    ]

    return {
        "total_predictions": total,
        "average_confidence": round(avg_conf, 4),
        "most_recognized_character": most_common,
        "recent_predictions": recent_list,
    }


def get_class_distribution():
    """Real per-class image counts, straight from the dataset inspection report."""
    if not Path(DATASET_REPORT_PATH).exists():
        return {}
    with open(DATASET_REPORT_PATH) as f:
        report = json.load(f)
    return report.get("per_class_counts", {})


def get_dataset_report():
    if not Path(DATASET_REPORT_PATH).exists():
        return None
    with open(DATASET_REPORT_PATH) as f:
        return json.load(f)


def get_model_metadata(filename="model_metadata.json"):
    metadata_path = Path(MODELS_DIR) / filename
    if not metadata_path.exists():
        return None
    with open(metadata_path) as f:
        return json.load(f)
