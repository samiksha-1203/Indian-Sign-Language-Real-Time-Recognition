"""
inference.py
============
Real-time inference pipeline:

    frame -> MediaPipe hand detection -> normalized landmarks -> landmark MLP
          -> confidence filter -> TemporalSmoother -> confirmed character

Also runnable standalone as a live webcam demo:
    python inference.py --models-dir ../models
"""

import argparse
import json
import time
from collections import Counter, deque
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf

DEFAULT_CONFIDENCE_THRESHOLD = 0.75
DEFAULT_WINDOW_SIZE = 7
DEFAULT_MIN_STABLE = 5
DEFAULT_COOLDOWN_SEC = 1.0


NUM_LANDMARKS = 21
FEATURES_PER_HAND = NUM_LANDMARKS * 3
MAX_HANDS = 2
LANDMARK_FEATURE_LEN = FEATURES_PER_HAND * MAX_HANDS + MAX_HANDS


def _normalize_hand(points_xyz):
    """Same normalization as extract_landmarks.py: wrist-centered, scaled by
    max distance from wrist to any landmark. Must stay IN SYNC with that
    script or the live model will see out-of-distribution features."""
    pts = np.array(points_xyz, dtype=np.float32)
    pts -= pts[0].copy()
    scale = np.linalg.norm(pts, axis=1).max()
    if scale < 1e-6:
        scale = 1e-6
    pts /= scale
    return pts.flatten()


def build_landmark_feature(landmark_sets_xyz, handedness_labels):
    """landmark_sets_xyz: list of hands, each a list of 21 [x,y,z].
    handedness_labels: parallel list of "Left"/"Right"/None.
    Returns a fixed-length feature vector matching extract_landmarks.py,
    or None if no usable hand is present."""
    if not landmark_sets_xyz:
        return None
    slots = {"Left": None, "Right": None}
    for points, label in zip(landmark_sets_xyz, handedness_labels):
        if label not in slots:
            continue
        slots[label] = _normalize_hand(points)

    feature = np.zeros(LANDMARK_FEATURE_LEN, dtype=np.float32)
    offset = 0
    for label in ("Left", "Right"):
        if slots[label] is not None:
            feature[offset:offset + FEATURES_PER_HAND] = slots[label]
            feature[FEATURES_PER_HAND * MAX_HANDS + (0 if label == "Left" else 1)] = 1.0
        offset += FEATURES_PER_HAND
    return feature


class LandmarkISLModel:
    """Classifies from normalized MediaPipe hand landmarks instead of pixels.
    No background/lighting/skin-tone in the input, and two-handed signs are
    handled natively (both hands' landmarks are concatenated) - this is the
    recommended primary model. See backend/ml/extract_landmarks.py and
    train_landmark.py for how it was trained.
    """

    def __init__(self, models_dir: str, model_file: str = "landmark_model.keras",
                 class_names_file: str = "landmark_class_names.json"):
        models_dir = Path(models_dir)
        model_path = models_dir / model_file
        if not model_path.exists():
            raise FileNotFoundError(
                f"No trained landmark model at {model_path}. Run "
                f"extract_landmarks.py then train_landmark.py first."
            )
        self.model = tf.keras.models.load_model(model_path)
        with open(models_dir / class_names_file) as f:
            self.class_names = json.load(f)

    def predict_from_landmarks(self, landmark_sets_xyz, handedness_labels):
        """Returns (predicted_class, confidence, full_probs) or (None, 0.0, None)
        if no usable hand landmarks were passed in."""
        feature = build_landmark_feature(landmark_sets_xyz, handedness_labels)
        if feature is None or feature.sum() == 0:
            return None, 0.0, None
        probs = self.model.predict(np.expand_dims(feature, axis=0), verbose=0)[0]
        idx = int(np.argmax(probs))
        return self.class_names[idx], float(probs[idx]), probs


class HandDetector:
    """Thin wrapper around MediaPipe Hands producing a padded, square ROI
    bounding box in pixel coordinates for the dominant detected hand.
    """

    def __init__(self, min_detection_confidence=0.6, min_tracking_confidence=0.5):
        self.mp_hands = getattr(getattr(mp, "solutions", None), "hands", None)
        self.hands = None
        self.landmarker = None
        self.last_landmarks = None
        self.last_landmark_sets_xyz = None
        self.last_handedness = None
        if self.mp_hands is not None:
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=min_detection_confidence,
                min_tracking_confidence=min_tracking_confidence,
            )
        else:
            from mediapipe.tasks import python as mp_python
            from mediapipe.tasks.python import vision

            model_path = Path(__file__).resolve().parents[1] / "models" / "hand_landmarker.task"
            if not model_path.exists():
                raise FileNotFoundError(
                    f"Hand detector model missing at {model_path}. "
                    "Download hand_landmarker.task before starting the API."
                )
            options = vision.HandLandmarkerOptions(
                base_options=mp_python.BaseOptions(model_asset_path=str(model_path)),
                running_mode=vision.RunningMode.IMAGE,
                num_hands=2,
                min_hand_detection_confidence=min_detection_confidence,
                min_hand_presence_confidence=min_detection_confidence,
                min_tracking_confidence=min_tracking_confidence,
            )
            self.landmarker = vision.HandLandmarker.create_from_options(options)

    def detect_roi(self, frame_bgr, padding_frac=0.35):
        h, w, _ = frame_bgr.shape
        self.last_landmarks = None
        self.last_landmark_sets_xyz = None
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        if self.hands is not None:
            results = self.hands.process(rgb)
            if not results.multi_hand_landmarks:
                self.last_handedness = None
                return None, None
            landmark_sets = [hand.landmark for hand in results.multi_hand_landmarks]
            self.last_handedness = [
                h.classification[0].label for h in results.multi_handedness
            ] if results.multi_handedness else [None] * len(landmark_sets)
        else:
            image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            results = self.landmarker.detect(image)
            if not results.hand_landmarks:
                self.last_handedness = None
                return None, None
            landmark_sets = results.hand_landmarks
            self.last_handedness = [
                h[0].category_name for h in results.handedness
            ] if results.handedness else [None] * len(landmark_sets)

        self.last_landmarks = [
            [[float(lm.x), float(lm.y)] for lm in landmarks]
            for landmarks in landmark_sets
        ]
        # Full x,y,z landmarks kept separately (with handedness) for the
        # landmark-based classifier - last_landmarks above stays 2D-only
        # since the frontend overlay already depends on that exact shape.
        self.last_landmark_sets_xyz = [
            [[float(lm.x), float(lm.y), float(lm.z)] for lm in landmarks]
            for landmarks in landmark_sets
        ]
        # Many ISL letters/numbers are two-handed and the dataset frames BOTH
        # hands together in a single crop. Build the ROI from the union of
        # every detected hand's landmarks (not just the largest hand) so a
        # two-handed sign is cropped the same way it was photographed for
        # training. For a single-hand sign this naturally collapses back to
        # that one hand's box.
        xs = [lm.x * w for landmarks in landmark_sets for lm in landmarks]
        ys = [lm.y * h for landmarks in landmark_sets for lm in landmarks]
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)

        box_w = x_max - x_min
        box_h = y_max - y_min
        side = int(max(box_w, box_h) * (1.0 + 2.0 * padding_frac))
        center_x = (x_min + x_max) // 2
        center_y = (y_min + y_max) // 2
        x_min = center_x - side // 2
        y_min = center_y - side // 2
        x_max = x_min + side
        y_max = y_min + side

        # Shift the square back inside the frame without changing its size.
        if x_min < 0:
            x_max -= x_min
            x_min = 0
        if y_min < 0:
            y_max -= y_min
            y_min = 0
        if x_max > w:
            x_min -= x_max - w
            x_max = w
        if y_max > h:
            y_min -= y_max - h
            y_max = h
        x_min = max(0, int(x_min))
        y_min = max(0, int(y_min))
        x_max = min(w, int(x_max))
        y_max = min(h, int(y_max))

        if x_max <= x_min or y_max <= y_min:
            return None, None

        roi = frame_bgr[y_min:y_max, x_min:x_max]
        return roi, (x_min, y_min, x_max, y_max)

    def close(self):
        if self.hands is not None:
            self.hands.close()
        if self.landmarker is not None:
            self.landmarker.close()


class TemporalSmoother:
    """Stateful per-session smoothing: rolling window + majority vote +
    confidence averaging + debounce/cooldown, so a held gesture produces
    exactly ONE confirmed character instead of a stream of repeats.
    """

    def __init__(self, window_size=DEFAULT_WINDOW_SIZE, min_stable=DEFAULT_MIN_STABLE,
                 cooldown_sec=DEFAULT_COOLDOWN_SEC, confidence_threshold=DEFAULT_CONFIDENCE_THRESHOLD):
        self.window_size = window_size
        self.min_stable = min_stable
        self.cooldown_sec = cooldown_sec
        self.confidence_threshold = confidence_threshold

        self.window = deque(maxlen=window_size)
        self.last_confirmed_char = None
        self.last_confirmed_time = 0.0
        self.in_neutral = True  # must return to neutral before repeating a char

    def reset(self):
        self.window.clear()
        self.last_confirmed_char = None
        self.last_confirmed_time = 0.0
        self.in_neutral = True

    def update(self, predicted_char, confidence, hand_present):
        """Call once per processed frame. Returns a dict describing the
        current display state and whether a NEW character was just confirmed.
        """
        now = time.time()

        if not hand_present:
            self.window.clear()
            self.in_neutral = True
            return {"display": None, "confidence": 0.0, "stable": False,
                    "confirmed": False, "confirmed_char": None,
                    "status": "no_hand"}

        if confidence < self.confidence_threshold:
            self.window.clear()
            return {"display": "Uncertain", "confidence": confidence, "stable": False,
                    "confirmed": False, "confirmed_char": None,
                    "status": "low_confidence"}

        self.window.append(predicted_char)

        counts = Counter(self.window)
        top_char, top_count = counts.most_common(1)[0]
        is_stable = len(self.window) >= self.min_stable and top_count >= self.min_stable

        if not is_stable:
            return {"display": predicted_char, "confidence": confidence, "stable": False,
                    "confirmed": False, "confirmed_char": None, "status": "collecting"}

        # Stable prediction. Only "confirm" (emit to sentence) if this is a
        # new gesture (different char, or we've passed through neutral +
        # cooldown since the last confirmation of the same char).
        cooldown_elapsed = (now - self.last_confirmed_time) >= self.cooldown_sec
        is_new_gesture = (top_char != self.last_confirmed_char) or self.in_neutral

        if is_new_gesture and cooldown_elapsed:
            self.last_confirmed_char = top_char
            self.last_confirmed_time = now
            self.in_neutral = False
            self.window.clear()
            return {"display": top_char, "confidence": confidence, "stable": True,
                    "confirmed": True, "confirmed_char": top_char, "status": "confirmed"}

        return {"display": top_char, "confidence": confidence, "stable": True,
                "confirmed": False, "confirmed_char": None, "status": "held"}


def run_webcam_demo(models_dir):
    """Standalone OpenCV demo window - useful for local testing on the
    RTX 2050 machine outside of the web app.
    """
    landmark_model = LandmarkISLModel(models_dir)
    detector = HandDetector()
    smoother = TemporalSmoother()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: could not open webcam.")
        return

    frame_count = 0
    infer_every_n_frames = 3  # throttle inference, not every frame
    last_result = {"display": None, "confidence": 0.0}
    sentence = ""

    print("Press 'q' to quit, 'c' to clear sentence.")
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)
        frame_count += 1

        roi, box = detector.detect_roi(frame)
        hand_present = roi is not None

        if hand_present and frame_count % infer_every_n_frames == 0:
            pred_char, conf, _ = landmark_model.predict_from_landmarks(
                detector.last_landmark_sets_xyz, detector.last_handedness
            )
            last_result = smoother.update(pred_char, conf, hand_present=True)
        elif not hand_present:
            last_result = smoother.update(None, 0.0, hand_present=False)

        if last_result.get("confirmed"):
            sentence += last_result["confirmed_char"]

        if box:
            x1, y1, x2, y2 = box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 200, 0), 2)

        cv2.putText(frame, f"Pred: {last_result.get('display')}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        cv2.putText(frame, f"Conf: {last_result.get('confidence', 0):.2f}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        cv2.putText(frame, f"Sentence: {sentence}", (10, 460),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)

        cv2.imshow("SignSpeak AI - Live Demo", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("c"):
            sentence = ""

    cap.release()
    cv2.destroyAllWindows()
    detector.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--models-dir", default="../models")
    args = parser.parse_args()
    run_webcam_demo(args.models_dir)
