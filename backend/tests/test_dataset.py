"""
test_dataset.py
================
Tests dataset discovery, class detection, corrupt-image handling and the
stratified split logic against small temporary fixture datasets (not the
full 42k-image dataset, so tests run fast).
"""

import sys
from pathlib import Path

import pytest
from PIL import Image

sys.path.append(str(Path(__file__).resolve().parent.parent / "ml"))

from dataset_inspector import inspect_dataset  # noqa: E402

# preprocess.py imports TensorFlow at module level (for tf.data pipelines),
# even though build_split_index() itself is pure Python/pathlib. Skip these
# split tests gracefully in environments without TensorFlow installed.
tf = pytest.importorskip("tensorflow")
from preprocess import build_split_index  # noqa: E402


@pytest.fixture
def tiny_dataset(tmp_path):
    """Creates classes A, B, C with 10/8/6 valid images plus one corrupted file."""
    counts = {"A": 10, "B": 8, "C": 6}
    for class_name, n in counts.items():
        class_dir = tmp_path / class_name
        class_dir.mkdir()
        for i in range(n):
            img = Image.new("RGB", (64, 64), color=(i * 10 % 255, 0, 0))
            img.save(class_dir / f"{i}.jpg")
    # one corrupted file in class A
    (tmp_path / "A" / "corrupt.jpg").write_bytes(b"not a real image")
    return tmp_path, counts


def test_dataset_discovery_finds_all_classes(tiny_dataset):
    dataset_path, counts = tiny_dataset
    report = inspect_dataset(dataset_path)
    assert report["total_classes"] == len(counts)
    assert set(report["class_names"]) == set(counts.keys())


def test_image_counts_match_real_files(tiny_dataset):
    dataset_path, counts = tiny_dataset
    report = inspect_dataset(dataset_path)
    for class_name, expected_count in counts.items():
        # +1 because the corrupted file is still counted as a file with a
        # valid extension, even though it fails to open
        expected = expected_count + 1 if class_name == "A" else expected_count
        assert report["per_class_counts"][class_name] == expected


def test_corrupted_image_detected(tiny_dataset):
    dataset_path, _ = tiny_dataset
    report = inspect_dataset(dataset_path)
    assert report["corrupted_count"] == 1
    assert "corrupt.jpg" in report["corrupted_images"][0]["path"]


def test_missing_dataset_path_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        inspect_dataset(tmp_path / "does_not_exist")


def test_dataset_with_no_class_folders_raises(tmp_path):
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    with pytest.raises(ValueError):
        inspect_dataset(empty_dir)


def test_stratified_split_covers_every_image(tiny_dataset):
    dataset_path, counts = tiny_dataset
    splits, class_names = build_split_index(dataset_path)
    total_split = len(splits["train"]) + len(splits["val"]) + len(splits["test"])
    # 25 valid images total (corrupt.jpg still gets included in the split
    # index since build_split_index doesn't open files - that's fine, it's
    # filtered out later at decode time in the tf.data pipeline)
    total_files = sum(counts.values()) + 1
    assert total_split == total_files
    assert set(class_names) == set(counts.keys())


def test_stratified_split_is_roughly_70_15_15(tiny_dataset):
    dataset_path, counts = tiny_dataset
    splits, _ = build_split_index(dataset_path, train_frac=0.70, val_frac=0.15)
    train_frac = len(splits["train"]) / sum(len(v) for v in splits.values())
    assert 0.55 <= train_frac <= 0.80  # loose bound given tiny per-class counts
