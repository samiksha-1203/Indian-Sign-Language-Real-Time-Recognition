"""
extract_landmarks.py
=====================
One-time offline pass: walks the existing ISL image dataset, runs MediaPipe
Hand Landmarker on every image, and writes out normalized landmark feature
vectors + labels to a single .npz file. This is the input for
train_landmark.py.

Why: pixel-based classification inherits background/lighting/skin-tone bias
from the training photos. Landmarks are geometry only, so they generalize
far better to new rooms, cameras and people, and they solve the two-hand
problem for free (each hand's landmarks are just concatenated).

Usage:
    python extract_landmarks.py --dataset-path ../../Indian --output ../datasets/landmarks.npz
"""

import argparse
import json
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

NUM_LANDMARKS = 21
FEATURES_PER_HAND = NUM_LANDMARKS * 3  # x, y, z
MAX_HANDS = 2
FEATURE_LEN = FEATURES_PER_HAND * MAX_HANDS + MAX_HANDS  # + a "hand present" flag per slot


def normalize_hand(landmarks):
    """landmarks: list of 21 (x, y, z) in image-normalized coords (0-1). Recenter
    on the wrist and scale-normalize so the feature is invariant to hand
    position in frame and distance from camera."""
    pts = np.array(landmarks, dtype=np.float32)  # (21, 3)
    wrist = pts[0].copy()
    pts -= wrist
    scale = np.linalg.norm(pts, axis=1).max()
    if scale < 1e-6:
        scale = 1e-6
    pts /= scale
    return pts.flatten()  # (63,)


def build_landmarker(min_detection_confidence=0.5):
    model_path = Path(__file__).resolve().parents[1] / "models" / "hand_landmarker.task"
    if not model_path.exists():
        raise FileNotFoundError(f"Hand detector model missing at {model_path}")
    options = vision.HandLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=str(model_path)),
        running_mode=vision.RunningMode.IMAGE,
        num_hands=2,
        min_hand_detection_confidence=min_detection_confidence,
        min_hand_presence_confidence=min_detection_confidence,
    )
    return vision.HandLandmarker.create_from_options(options)


def extract_from_image(landmarker, image_bgr):
    """Returns a fixed-length feature vector or None if no hand detected.
    Hand slots are ordered Left-then-Right (by MediaPipe's handedness label)
    so the same physical hand always lands in the same feature slot."""
    rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    result = landmarker.detect(mp_image)

    if not result.hand_landmarks:
        return None

    slots = {"Left": None, "Right": None}
    for hand_landmarks, handedness in zip(result.hand_landmarks, result.handedness):
        label = handedness[0].category_name  # "Left" or "Right"
        pts = [[lm.x, lm.y, lm.z] for lm in hand_landmarks]
        slots[label] = normalize_hand(pts)

    feature = np.zeros(FEATURE_LEN, dtype=np.float32)
    offset = 0
    for label in ("Left", "Right"):
        if slots[label] is not None:
            feature[offset:offset + FEATURES_PER_HAND] = slots[label]
            feature[FEATURES_PER_HAND * MAX_HANDS + (0 if label == "Left" else 1)] = 1.0
        offset += FEATURES_PER_HAND
    return feature


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-path", default="../../Indian")
    parser.add_argument("--output", default="../datasets/landmarks.npz")
    parser.add_argument("--min-detection-confidence", type=float, default=0.5)
    parser.add_argument("--limit-per-class", type=int, default=None,
                         help="Optional cap per class, useful for a fast smoke test")
    parser.add_argument("--class-start", type=int, default=0)
    parser.add_argument("--class-end", type=int, default=None,
                         help="Exclusive end index into sorted class list, for chunked runs")
    args = parser.parse_args()

    dataset_path = Path(args.dataset_path)
    all_class_names = sorted([d.name for d in dataset_path.iterdir() if d.is_dir()])
    class_end = args.class_end if args.class_end is not None else len(all_class_names)
    class_names = all_class_names[args.class_start:class_end]

    landmarker = build_landmarker(args.min_detection_confidence)

    features, labels, paths = [], [], []
    skipped = 0

    for offset_idx, class_name in enumerate(class_names):
        label_idx = args.class_start + offset_idx  # absolute index into all_class_names
        class_dir = dataset_path / class_name
        files = sorted(
            p for p in class_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}
        )
        if args.limit_per_class:
            files = files[: args.limit_per_class]
        print(f"[{class_name}] {len(files)} images...", flush=True)
        for f in files:
            img = cv2.imread(str(f))
            if img is None:
                skipped += 1
                continue
            feat = extract_from_image(landmarker, img)
            if feat is None:
                skipped += 1
                continue
            features.append(feat)
            labels.append(label_idx)
            paths.append(str(f))

    features = np.stack(features)
    labels = np.array(labels, dtype=np.int64)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.output, features=features, labels=labels, paths=np.array(paths))
    classes_path = Path(args.output).with_name(Path(args.output).stem + ".classes.json")
    with open(classes_path, "w") as f:
        json.dump(all_class_names, f, indent=2)  # always the FULL class list, for consistent label indices

    print(f"\nDone. {len(features)} usable samples, {skipped} skipped (no hand detected).")
    print(f"Feature dim: {features.shape[1]}  Classes: {len(class_names)}")
    print(f"Saved: {args.output}")
    print(f"Saved: {classes_path}")


if __name__ == "__main__":
    main()
