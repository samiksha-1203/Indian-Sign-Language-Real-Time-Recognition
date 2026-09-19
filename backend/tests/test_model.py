"""Tests for the active landmark MLP."""

import sys
from pathlib import Path

import numpy as np
import pytest

tf = pytest.importorskip("tensorflow")

sys.path.append(str(Path(__file__).resolve().parent.parent / "ml"))

from landmark_model import build_landmark_model  # noqa: E402


def test_landmark_model_output_shape_matches_num_classes():
    model = build_landmark_model(input_dim=128, num_classes=35)
    assert model.output_shape == (None, 35)


def test_landmark_model_input_shape_matches_feature_dim():
    model = build_landmark_model(input_dim=128, num_classes=5)
    assert model.input_shape == (None, 128)


def test_landmark_model_predicts_probability_distribution():
    model = build_landmark_model(input_dim=128, num_classes=4)
    dummy_batch = np.random.normal(size=(2, 128)).astype("float32")
    predictions = model.predict(dummy_batch, verbose=0)
    assert predictions.shape == (2, 4)
    np.testing.assert_allclose(predictions.sum(axis=1), np.ones(2), atol=1e-4)


def test_landmark_model_save_and_load_roundtrip(tmp_path):
    model = build_landmark_model(input_dim=128, num_classes=3)
    save_path = tmp_path / "test_landmark_model.keras"
    model.save(save_path)

    loaded = tf.keras.models.load_model(save_path)
    dummy = np.random.normal(size=(1, 128)).astype("float32")
    original_prediction = model.predict(dummy, verbose=0)
    loaded_prediction = loaded.predict(dummy, verbose=0)
    np.testing.assert_allclose(original_prediction, loaded_prediction, atol=1e-5)
