"""
main.py
=======
FastAPI application entrypoint.

    uvicorn app.main:app --reload --port 8000

The ML model is loaded ONCE (via app.services.predictor.predictor_service,
a module-level singleton) at import time / startup - never per-request.
"""

import tensorflow as tf
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS, DATASET_DIR
from app.database import init_db
from app.schemas import HealthResponse
from app.services.predictor import predictor_service
from app.routes import prediction, sentence, analytics, model, speech

app = FastAPI(
    title="SignSpeak AI API",
    description="Real-time Indian Sign Language recognition, sentence building and speech.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()
    # predictor_service is already instantiated at import time (module-level
    # singleton) so the model is loaded exactly once before the first request.


@app.get("/health", response_model=HealthResponse)
def health():
    gpu_available = len(tf.config.list_physical_devices("GPU")) > 0
    return HealthResponse(
        status="ok",
        model_loaded=predictor_service.is_loaded,
        gpu_available=gpu_available,
        dataset_available=DATASET_DIR.exists(),
    )


app.include_router(prediction.router)
app.include_router(sentence.router)
app.include_router(analytics.router)
app.include_router(model.router)
app.include_router(speech.router)
