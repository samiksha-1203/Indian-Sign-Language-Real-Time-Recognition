"""
schemas.py
==========
Pydantic models for request validation and response shapes.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field


# ---------- Prediction ----------

class PredictStaticRequest(BaseModel):
    session_id: str = Field(..., description="Client session id, groups smoothing state")
    image_base64: str = Field(..., description="Base64-encoded JPEG/PNG frame from the webcam")
    confidence_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)


class PredictStaticResponse(BaseModel):
    status: str  # "no_hand" | "low_confidence" | "collecting" | "held" | "confirmed"
    display: Optional[str] = None
    confidence: float = 0.0
    stable: bool = False
    confirmed: bool = False
    confirmed_char: Optional[str] = None
    hand_box: Optional[List[int]] = None
    hand_landmarks: Optional[List[List[List[float]]]] = None


# ---------- Sentence ----------

class SentenceCreateResponse(BaseModel):
    session_id: str
    sentence: str = ""


class SentenceAddRequest(BaseModel):
    session_id: str
    character: str


class SessionIdRequest(BaseModel):
    session_id: str


class SentenceResponse(BaseModel):
    session_id: str
    sentence: str


# ---------- Speech ----------

class SpeakRequest(BaseModel):
    text: str


class SpeakResponse(BaseModel):
    status: str
    text: str


# ---------- Model / Dataset info ----------

class ModelInfoResponse(BaseModel):
    model_name: Optional[str]
    framework: str = "TensorFlow / Keras"
    architecture: Optional[str] = None
    feature_dim: Optional[int] = None
    input_shape: Optional[List[int]] = None
    num_classes: Optional[int] = None
    classes: Optional[List[str]] = None
    dataset: Optional[str] = None
    test_accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1: Optional[float] = None
    model_size_mb: Optional[float] = None
    training_date: Optional[str] = None
    model_loaded: bool


class DatasetInfoResponse(BaseModel):
    dataset_path: Optional[str] = None
    total_classes: Optional[int] = None
    total_images: Optional[int] = None
    per_class_counts: Optional[Dict[str, int]] = None
    image_formats: Optional[Dict[str, int]] = None
    image_dimensions: Optional[Dict[str, Any]] = None
    corrupted_count: Optional[int] = None
    duplicate_files: Optional[int] = None
    class_imbalance: Optional[Dict[str, Any]] = None
    report_available: bool


# ---------- Analytics ----------

class AnalyticsSummaryResponse(BaseModel):
    total_predictions: int
    average_confidence: float
    most_recognized_character: Optional[str]
    recent_predictions: List[Dict[str, Any]]


class ClassAnalyticsResponse(BaseModel):
    class_distribution: Dict[str, int]


# ---------- Health ----------

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    gpu_available: bool
    dataset_available: bool
