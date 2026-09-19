"""
train_landmark.py
==================
Trains the landmark-based MLP on the output of extract_landmarks.py.

Usage:
    python extract_landmarks.py                 # writes ../datasets/landmarks.npz
    python train_landmark.py                    # trains + evaluates

Uses the SAME contiguous-block split policy as preprocess.py (no shuffling
before splitting) because these are still sequential burst-capture frames
per class - shuffling first would leak near-duplicate frames across
train/val/test exactly like the original pixel-model bug.
"""

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import tensorflow as tf
from sklearn.metrics import confusion_matrix, classification_report

from landmark_model import build_landmark_model


def contiguous_split(features, labels, train_frac=0.70, val_frac=0.15):
    """Per-class contiguous block split (matches preprocess.build_split_index)."""
    idx_by_class = {}
    for i, label in enumerate(labels):
        idx_by_class.setdefault(int(label), []).append(i)

    train_idx, val_idx, test_idx = [], [], []
    for label, idxs in idx_by_class.items():
        n = len(idxs)
        n_train = int(n * train_frac)
        n_val = int(n * val_frac)
        train_idx += idxs[:n_train]
        val_idx += idxs[n_train:n_train + n_val]
        test_idx += idxs[n_train + n_val:]

    return (
        (features[train_idx], labels[train_idx]),
        (features[val_idx], labels[val_idx]),
        (features[test_idx], labels[test_idx]),
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--landmarks-path", default="../datasets/landmarks.npz")
    parser.add_argument("--classes-path", default="../datasets/landmarks.classes.json")
    parser.add_argument("--models-dir", default="../models")
    parser.add_argument("--epochs", type=int, default=60)
    parser.add_argument("--batch-size", type=int, default=64)
    args = parser.parse_args()

    models_dir = Path(args.models_dir)
    models_dir.mkdir(parents=True, exist_ok=True)

    data = np.load(args.landmarks_path)
    features, labels = data["features"], data["labels"]
    with open(args.classes_path) as f:
        class_names = json.load(f)
    num_classes = len(class_names)

    print(f"Loaded {len(features)} samples, {features.shape[1]} features, {num_classes} classes")

    (x_train, y_train), (x_val, y_val), (x_test, y_test) = contiguous_split(features, labels)
    print(f"Split -> train:{len(x_train)} val:{len(x_val)} test:{len(x_test)}")

    model = build_landmark_model(features.shape[1], num_classes)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    model.summary()

    checkpoint_path = models_dir / "landmark_model.keras"
    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(str(checkpoint_path), monitor="val_accuracy",
                                            save_best_only=True, verbose=1),
        tf.keras.callbacks.EarlyStopping(monitor="val_accuracy", patience=10,
                                          restore_best_weights=True),
        tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=5),
    ]

    model.fit(
        x_train, y_train,
        validation_data=(x_val, y_val),
        epochs=args.epochs,
        batch_size=args.batch_size,
        callbacks=callbacks,
        verbose=2,
    )

    test_loss, test_accuracy = model.evaluate(x_test, y_test, verbose=0)
    print(f"\nTest loss: {test_loss:.4f} | Test accuracy: {test_accuracy:.4f}")

    y_pred = np.argmax(model.predict(x_test, verbose=0), axis=1)
    report = classification_report(y_test, y_pred, target_names=class_names, output_dict=True)
    cm = confusion_matrix(y_test, y_pred)

    plt.figure(figsize=(14, 12))
    sns.heatmap(cm, xticklabels=class_names, yticklabels=class_names, cmap="Blues")
    plt.title("ISL Landmark Classification - Confusion Matrix (Test Set)")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()
    plt.savefig(models_dir / "landmark_confusion_matrix.png", dpi=150)

    with open(models_dir / "landmark_class_names.json", "w") as f:
        json.dump(class_names, f, indent=2)

    metadata = {
        "model_name": "isl_landmark_mlp",
        "feature_dim": int(features.shape[1]),
        "num_classes": num_classes,
        "train_size": len(x_train),
        "val_size": len(x_val),
        "test_size": len(x_test),
        "test_accuracy": float(test_accuracy),
        "test_loss": float(test_loss),
        "macro_f1": report["macro avg"]["f1-score"],
        "weighted_f1": report["weighted avg"]["f1-score"],
    }
    with open(models_dir / "landmark_model_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nSaved: {checkpoint_path}")
    print(f"Saved: {models_dir / 'landmark_confusion_matrix.png'}")
    print(f"Saved: {models_dir / 'landmark_model_metadata.json'}")
    print(f"\nMacro F1: {metadata['macro_f1']:.4f}  Weighted F1: {metadata['weighted_f1']:.4f}")


if __name__ == "__main__":
    main()
