"""Model training pipeline."""

import logging
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit
from xgboost import XGBClassifier

from charliehustle.data.features import FEATURE_COLUMNS, TARGET_COLUMN

logger = logging.getLogger(__name__)


def train_model(
    features: pd.DataFrame,
    model_path: Path | None = None,
    n_splits: int = 5,
) -> XGBClassifier:
    """Train an XGBoost model with time-series cross-validation.

    Trains on FEATURE_COLUMNS to predict TARGET_COLUMN (home_win).
    """
    X = features[FEATURE_COLUMNS].values
    y = features[TARGET_COLUMN].values

    logger.info(f"Training on {len(X)} samples with {X.shape[1]} features")

    tscv = TimeSeriesSplit(n_splits=n_splits)
    cv_scores = []

    for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
        X_train, X_val = X[train_idx], X[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]

        model = XGBClassifier(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.1,
            reg_lambda=1.0,
            eval_metric="logloss",
            random_state=42,
        )
        model.fit(
            X_train,
            y_train,
            eval_set=[(X_val, y_val)],
            verbose=False,
        )
        score = model.score(X_val, y_val)
        cv_scores.append(score)
        logger.info(f"  Fold {fold + 1}: accuracy = {score:.4f}")

    logger.info(
        f"CV accuracy: {np.mean(cv_scores):.4f} +/- {np.std(cv_scores):.4f}"
    )

    # Train final model on all data
    final_model = XGBClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=1.0,
        eval_metric="logloss",
        random_state=42,
    )
    final_model.fit(X, y, verbose=False)

    if model_path:
        model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(final_model, model_path)
        logger.info(f"Model saved to {model_path}")

    return final_model


def load_model(model_path: Path) -> XGBClassifier:
    """Load a trained model from disk."""
    return joblib.load(model_path)
