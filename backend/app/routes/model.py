"""
model.py (routes)
==================
GET /model-info, GET /dataset-info - read real metadata/report files from
disk. Never invents numbers.
"""

from pathlib import Path

from fastapi import APIRouter

from app.config import MODELS_DIR
from app.schemas import ModelInfoResponse, DatasetInfoResponse
from app.services.predictor import predictor_service
from app.services import analytics as analytics_service

router = APIRouter(tags=["model"])


@router.get("/model-info", response_model=ModelInfoResponse)
def model_info():
    metadata = analytics_service.get_model_metadata("landmark_model_metadata.json")
    model_path = Path(MODELS_DIR) / "landmark_model.keras"
    size_mb = round(model_path.stat().st_size / (1024 * 1024), 2) if model_path.exists() else None

    if metadata is None:
        return ModelInfoResponse(
            model_name=None, input_shape=None, num_classes=None, classes=None,
            dataset=None, test_accuracy=None, precision=None, recall=None, f1=None,
            architecture=None, feature_dim=None, model_size_mb=size_mb, training_date=None,
            model_loaded=predictor_service.is_loaded,
        )

    img_size = metadata.get("img_size")
    feature_dim = metadata.get("feature_dim")
    classes = metadata.get("classes")
    if classes is None:
        classes = predictor_service.class_names
    return ModelInfoResponse(
        model_name=metadata.get("model_name"),
        architecture="MediaPipe landmarks + MLP",
        feature_dim=feature_dim,
        input_shape=([img_size, img_size, 3] if img_size else [feature_dim] if feature_dim else None),
        num_classes=metadata.get("num_classes"),
        classes=classes,
        dataset=metadata.get("dataset", "Indian Sign Language (ISL)"),
        test_accuracy=metadata.get("test_accuracy"),
        precision=metadata.get("precision"),
        recall=metadata.get("recall"),
        f1=metadata.get("f1", metadata.get("macro_f1")),
        model_size_mb=size_mb,
        training_date=metadata.get("training_date"),
        model_loaded=predictor_service.is_loaded,
    )


@router.get("/dataset-info", response_model=DatasetInfoResponse)
def dataset_info():
    report = analytics_service.get_dataset_report()
    if report is None:
        return DatasetInfoResponse(report_available=False)

    return DatasetInfoResponse(
        dataset_path=report.get("dataset_path"),
        total_classes=report.get("total_classes"),
        total_images=report.get("total_images"),
        per_class_counts=report.get("per_class_counts"),
        image_formats=report.get("image_formats"),
        image_dimensions=report.get("image_dimensions"),
        corrupted_count=report.get("corrupted_count"),
        duplicate_files=report.get("duplicate_files"),
        class_imbalance=report.get("class_imbalance"),
        report_available=True,
    )
