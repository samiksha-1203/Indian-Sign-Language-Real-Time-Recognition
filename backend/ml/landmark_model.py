"""
landmark_model.py
==================
A small MLP that classifies ISL signs from normalized MediaPipe hand
landmarks instead of raw pixels. No background, lighting, or skin tone in
the input at all, so it can't pick up the shortcuts that bit the pixel
model (background-correlated classes, single-hand crop of two-handed
signs). Trains in minutes on CPU.
"""

import tensorflow as tf


def build_landmark_model(input_dim, num_classes):
    inputs = tf.keras.Input(shape=(input_dim,))
    x = tf.keras.layers.Dense(256, activation="relu")(inputs)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    x = tf.keras.layers.Dense(128, activation="relu")(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    x = tf.keras.layers.Dense(64, activation="relu")(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    outputs = tf.keras.layers.Dense(num_classes, activation="softmax")(x)
    return tf.keras.Model(inputs, outputs, name="isl_landmark_mlp")
