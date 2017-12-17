from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='3'

import numpy as np
import pandas as pd
import tensorflow as tf

# Data sets
MLB_TRAIN = "data/train/mlb_train.csv"
MLB_TEST = "data/test/mlb_test.csv"

feature_columns = feature_columns = [tf.feature_column.numeric_column("x", shape=[8])]
classifier = None

def init():
    global classifier

    if classifier is None:
        classifier = tf.estimator.LinearClassifier(
        feature_columns=feature_columns,
        model_dir="/tmp/mlb_picks_model")

def train(numSteps):
    global classifier

    training_set = tf.contrib.learn.datasets.base.load_csv_with_header(
    filename=MLB_TRAIN,
    target_dtype=np.int,
    features_dtype=np.float32)

    # Define the training inputs
    train_input_fn = tf.estimator.inputs.numpy_input_fn(
    x={"x": np.array(training_set.data)},
    y=np.array(training_set.target),
    num_epochs=None,
    shuffle=True)

    # Train model.
    print("Training model...")
    classifier.train(input_fn=train_input_fn, steps=numSteps)

def test():
    global classifier

    test_set = tf.contrib.learn.datasets.base.load_csv_with_header(
    filename=MLB_TEST,
    target_dtype=np.int,
    features_dtype=np.float32)

    # Define the test inputs
    test_input_fn = tf.estimator.inputs.numpy_input_fn(
    x={"x": np.array(test_set.data)},
    y=np.array(test_set.target),
    num_epochs=1,
    shuffle=False)

    # Evaluate accuracy.
    print("Evaluating model...")
    ev = classifier.evaluate(input_fn=test_input_fn)
    print("Loss: %s" % ev["loss"])
    print("\nTest Accuracy: {0:f}\n".format(ev["accuracy"]))

def predict(gameData):
    global classifier
    init()

    data = np.array([gameData], dtype=np.float32)
    predict_input_fn = tf.estimator.inputs.numpy_input_fn(
    x={"x": data},
    num_epochs=1,
    shuffle=False)

    predictions = list(classifier.predict(input_fn=predict_input_fn))
    prediction = predictions[0]

    pick = int(prediction["classes"][0])
    probs = prediction["probabilities"]
    return pick,probs[0],probs[1]

def main():
    init()
    train(10000)
    test()

if __name__ == "__main__":
    main()
