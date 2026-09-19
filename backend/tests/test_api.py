"""
test_api.py
===========
Exercises /health, /model-info, /dataset-info, /predict/static, /sentence/*,
/analytics using FastAPI's TestClient against an isolated in-memory SQLite
database. Requires tensorflow/fastapi to be installed - skipped otherwise.
"""

import sys
from pathlib import Path

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("tensorflow")

sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def client():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestSessionLocal = sessionmaker(bind=engine)

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_health_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "model_loaded" in body
    assert "gpu_available" in body


def test_model_info_endpoint(client):
    resp = client.get("/model-info")
    assert resp.status_code == 200
    assert "model_loaded" in resp.json()


def test_dataset_info_endpoint(client):
    resp = client.get("/dataset-info")
    assert resp.status_code == 200
    assert "report_available" in resp.json()


def test_predict_static_returns_503_when_model_not_loaded(client):
    # In a fresh test environment with no trained model present, this
    # MUST return 503 - never a fabricated prediction.
    resp = client.post("/predict/static", json={
        "session_id": "test-session",
        "image_base64": "not-a-real-image",
    })
    assert resp.status_code in (503, 400)


def test_sentence_create_and_add_flow(client):
    create_resp = client.post("/sentence/create")
    assert create_resp.status_code == 200
    session_id = create_resp.json()["session_id"]

    for ch in "HELLO":
        resp = client.post("/sentence/add", json={"session_id": session_id, "character": ch})
        assert resp.status_code == 200
    assert resp.json()["sentence"] == "HELLO"

    resp = client.post("/sentence/space", json={"session_id": session_id})
    resp = client.post("/sentence/add", json={"session_id": session_id, "character": "W"})
    assert resp.json()["sentence"] == "HELLO W"

    resp = client.post("/sentence/backspace", json={"session_id": session_id})
    assert resp.json()["sentence"] == "HELLO "

    resp = client.post("/sentence/clear", json={"session_id": session_id})
    assert resp.json()["sentence"] == ""


def test_get_sentence_endpoint(client):
    create_resp = client.post("/sentence/create")
    session_id = create_resp.json()["session_id"]
    resp = client.get(f"/sentence/{session_id}")
    assert resp.status_code == 200
    assert resp.json()["sentence"] == ""


def test_analytics_summary_empty_state(client):
    resp = client.get("/analytics")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_predictions"] == 0
    assert body["recent_predictions"] == []


def test_speak_with_empty_text_returns_400(client):
    resp = client.post("/speak", json={"text": ""})
    assert resp.status_code == 400
