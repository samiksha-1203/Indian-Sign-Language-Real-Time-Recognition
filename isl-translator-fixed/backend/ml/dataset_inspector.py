"""
dataset_inspector.py
=====================
Recursively inspects the locally extracted Indian Sign Language (ISL)
dataset and computes REAL statistics -- nothing here is hard-coded.

Usage:
    python dataset_inspector.py --dataset-path ../datasets/ISL --output ../datasets/dataset_report.json
"""

import argparse
import hashlib
import json
import os
from collections import defaultdict
from pathlib import Path

from PIL import Image

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def sha256_of_file(path, block_size=65536):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            block = f.read(block_size)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def inspect_dataset(dataset_path: Path):
    """Walk the dataset directory. Assumes ImageFolder-style layout:
    dataset_path/<class_name>/<image files>
    """
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset path not found: {dataset_path}")

    class_dirs = sorted(
        [d for d in dataset_path.iterdir() if d.is_dir()],
        key=lambda p: p.name,
    )

    if not class_dirs:
        raise ValueError(
            f"No class subfolders found under {dataset_path}. "
            "Expected an ImageFolder-style layout (dataset_path/<class>/<images>)."
        )

    per_class_counts = {}
    format_counts = defaultdict(int)
    dims_seen = defaultdict(int)
    min_dim = None
    max_dim = None
    corrupted = []
    hash_to_paths = defaultdict(list)
    total_images = 0

    for class_dir in class_dirs:
        class_name = class_dir.name
        count = 0
        for file_path in sorted(class_dir.iterdir()):
            if not file_path.is_file():
                continue
            ext = file_path.suffix.lower()
            if ext not in VALID_EXTENSIONS:
                continue

            count += 1
            total_images += 1
            format_counts[ext.replace(".", "").upper()] += 1

            # Try to open + validate the image
            try:
                with Image.open(file_path) as img:
                    img.verify()
                # re-open after verify() (verify() invalidates the file handle)
                with Image.open(file_path) as img:
                    w, h = img.size
                    dims_seen[(w, h)] += 1
                    if min_dim is None or (w * h) < (min_dim[0] * min_dim[1]):
                        min_dim = (w, h)
                    if max_dim is None or (w * h) > (max_dim[0] * max_dim[1]):
                        max_dim = (w, h)
            except Exception as e:
                corrupted.append({"path": str(file_path), "error": str(e)})
                continue

            # Duplicate detection via content hash (only for reasonably small sets;
            # this dataset is small enough - ~40k images - that this is practical)
            try:
                file_hash = sha256_of_file(file_path)
                hash_to_paths[file_hash].append(str(file_path))
            except Exception:
                pass

        per_class_counts[class_name] = count

    duplicates = {h: paths for h, paths in hash_to_paths.items() if len(paths) > 1}
    num_duplicate_files = sum(len(v) - 1 for v in duplicates.values())

    most_common_dim = max(dims_seen.items(), key=lambda kv: kv[1])[0] if dims_seen else None

    counts = list(per_class_counts.values())
    imbalance = {
        "min_class_count": min(counts) if counts else 0,
        "max_class_count": max(counts) if counts else 0,
        "mean_class_count": (sum(counts) / len(counts)) if counts else 0,
        "imbalance_ratio": (max(counts) / min(counts)) if counts and min(counts) > 0 else None,
    }

    report = {
        "dataset_path": str(dataset_path.resolve()),
        "total_classes": len(class_dirs),
        "total_images": total_images,
        "class_names": [d.name for d in class_dirs],
        "per_class_counts": per_class_counts,
        "image_formats": dict(format_counts),
        "image_dimensions": {
            "minimum": min_dim,
            "maximum": max_dim,
            "most_common": most_common_dim,
            "unique_dimension_count": len(dims_seen),
        },
        "corrupted_images": corrupted,
        "corrupted_count": len(corrupted),
        "duplicate_groups": len(duplicates),
        "duplicate_files": num_duplicate_files,
        "class_imbalance": imbalance,
    }
    return report


def print_report(report):
    print("=" * 60)
    print("ISL DATASET INSPECTION")
    print("=" * 60)
    print(f"\nDataset Path: {report['dataset_path']}")
    print(f"Total Classes: {report['total_classes']}")
    print(f"Total Images: {report['total_images']}")

    print("\nClasses:\n")
    letters = sorted([c for c in report["class_names"] if c.isalpha()])
    digits = sorted([c for c in report["class_names"] if c.isdigit()], key=int)
    for c in letters:
        print(f"{c} -> {report['per_class_counts'][c]}")
    for c in digits:
        print(f"{c} -> {report['per_class_counts'][c]}")

    print("\nImage Formats:")
    for fmt, n in report["image_formats"].items():
        print(f"{fmt}: {n}")

    print("\nImage Dimensions:")
    print(f"Minimum: {report['image_dimensions']['minimum']}")
    print(f"Maximum: {report['image_dimensions']['maximum']}")
    print(f"Most Common: {report['image_dimensions']['most_common']}")

    print(f"\nCorrupted Images: {report['corrupted_count']}")
    print(f"Duplicate Images: {report['duplicate_files']} (in {report['duplicate_groups']} groups)")

    print("\nClass Imbalance:")
    imb = report["class_imbalance"]
    print(f"  min class count: {imb['min_class_count']}")
    print(f"  max class count: {imb['max_class_count']}")
    print(f"  mean class count: {imb['mean_class_count']:.1f}")
    print(f"  imbalance ratio (max/min): {imb['imbalance_ratio']}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Inspect the ISL dataset")
    parser.add_argument("--dataset-path", type=str, default="../datasets/ISL")
    parser.add_argument("--output", type=str, default="../datasets/dataset_report.json")
    args = parser.parse_args()

    dataset_path = Path(args.dataset_path)
    report = inspect_dataset(dataset_path)
    print_report(report)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nFull report saved to: {output_path.resolve()}")


if __name__ == "__main__":
    main()
