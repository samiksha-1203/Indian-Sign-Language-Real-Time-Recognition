"""
predictor.py (service)
=======================
Wraps the ml/inference.py pipeline for use inside FastAPI. The model and
MediaPipe hand detector are loaded ONCE at app startup and kept in memory.
Temporal smoothing state is kept per session_id so concurrent users (or a
page refresh mid-sentence) don't interfere with each other.
"""

import base64
import io
import sys
from pathlib import Path
from threading import Lock

import cv2
import numpy as np
from PIL import Image

sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "ml"))

from app.config import (  # noqa: E402
    MODELS_DIR, CONFIDENCE_THRESHOLD_DEFAULT,
    SMOOTHING_WINDOW_SIZE, SMOOTHING_MIN_STABLE, SMOOTHING_COOLDOWN_SEC,
)


class PredictorService:
    def __init__(self):
        self._landmark_model = None
        self._detector = None
        self._load_error = None
        self._smoothers = {}  # session_id -> TemporalSmoother
        self._lock = Lock()
        self._try_load()

    def _try_load(self):
        try:
            from inference import LandmarkISLModel, HandDetector  # local import, ml/ on sys.path
            self._detector = HandDetector()
            self._landmark_model = LandmarkISLModel(str(MODELS_DIR))
        except Exception as e:
            self._load_error = str(e)
            self._landmark_model = None
            self._detector = None

    @property
    def is_loaded(self):
        return self._detector is not None and self._landmark_model is not None

    @property
    def using_landmark_model(self):
        return self._landmark_model is not None

    @property
    def load_error(self):
        return self._load_error

    @property
    def class_names(self):
        return self._landmark_model.class_names if self._landmark_model else []

    def _get_smoother(self, session_id, confidence_threshold=None):
        from inference import TemporalSmoother
        with self._lock:
            if session_id not in self._smoothers:
                self._smoothers[session_id] = TemporalSmoother(
                    window_size=SMOOTHING_WINDOW_SIZE,
                    min_stable=SMOOTHING_MIN_STABLE,
                    cooldown_sec=SMOOTHING_COOLDOWN_SEC,
                    confidence_threshold=confidence_threshold or CONFIDENCE_THRESHOLD_DEFAULT,
                )
            return self._smoothers[session_id]

    @staticmethod
    def _decode_base64_image(image_base64: str) -> np.ndarray:
        if "," in image_base64 and image_base64.strip().startswith("data:"):
            image_base64 = image_base64.split(",", 1)[1]
        raw = base64.b64decode(image_base64)
        pil_img = Image.open(io.BytesIO(raw)).convert("RGB")
        frame = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        return frame

    def predict_frame(self, session_id: str, image_base64: str, confidence_threshold=None):
        if not self.is_loaded:
            raise RuntimeError(f"Model not loaded: {self._load_error}")

        frame = self._decode_base64_image(image_base64)
        roi, box = self._detector.detect_roi(frame)
        smoother = self._get_smoother(session_id, confidence_threshold)

        if roi is None or roi.size == 0:
            result = smoother.update(None, 0.0, hand_present=False)
            result["hand_box"] = None
            return result

        if self._landmark_model is not None and self._detector.last_landmark_sets_xyz:
            pred_char, confidence, _probs = self._landmark_model.predict_from_landmarks(
                self._detector.last_landmark_sets_xyz, self._detector.last_handedness
            )
            if pred_char is None:
                pred_char, confidence = None, 0.0
        else:
            pred_char, confidence = None, 0.0

        result = smoother.update(pred_char, confidence, hand_present=True)
        result["hand_box"] = list(box)
        result["hand_landmarks"] = self._detector.last_landmarks
        return result

    def reset_session(self, session_id: str):
        with self._lock:
            self._smoothers.pop(session_id, None)


# Singleton instance used by routes (loaded once at import / app startup)
predictor_service = PredictorService()
