"""Model evaluation metrics."""

import logging

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, brier_score_loss, log_loss

logger = logging.getLogger(__name__)


def evaluate_predictions(games: pd.DataFrame) -> dict[str, float]:
    """Evaluate model predictions against actual outcomes.

    Expects columns: home_win, model_home_prob.
    """
    y_true = games["home_win"].values
    y_prob = games["model_home_prob"].values
    y_pred = (y_prob >= 0.5).astype(int)

    metrics: dict[str, float] = {
        "accuracy": accuracy_score(y_true, y_pred),
        "brier_score": brier_score_loss(y_true, y_prob),
        "log_loss": log_loss(y_true, y_prob),
        "n_games": len(games),
        "home_win_rate": y_true.mean(),
        "predicted_home_rate": y_pred.mean(),
    }

    # Calibration by bucket
    for bucket_name, lo, hi in [
        ("low", 0.0, 0.4),
        ("mid", 0.4, 0.6),
        ("high", 0.6, 1.0),
    ]:
        mask = (y_prob >= lo) & (y_prob < hi)
        if mask.sum() > 0:
            metrics[f"calibration_{bucket_name}_pred"] = y_prob[mask].mean()
            metrics[f"calibration_{bucket_name}_actual"] = y_true[mask].mean()
            metrics[f"calibration_{bucket_name}_n"] = int(mask.sum())

    return metrics


def print_evaluation(metrics: dict[str, float]) -> None:
    """Print evaluation metrics in a readable format."""
    print(f"\n{'=' * 50}")
    print(f"  Model Evaluation ({metrics['n_games']:.0f} games)")
    print(f"{'=' * 50}")
    print(f"  Accuracy:        {metrics['accuracy']:.1%}")
    print(f"  Brier Score:     {metrics['brier_score']:.4f}")
    print(f"  Log Loss:        {metrics['log_loss']:.4f}")
    print(f"  Home Win Rate:   {metrics['home_win_rate']:.1%}")
    print(f"  Predicted Home:  {metrics['predicted_home_rate']:.1%}")
    print()
    print("  Calibration:")
    for bucket in ["low", "mid", "high"]:
        key = f"calibration_{bucket}_n"
        if key in metrics:
            pred = metrics[f"calibration_{bucket}_pred"]
            actual = metrics[f"calibration_{bucket}_actual"]
            n = metrics[key]
            print(
                f"    {bucket:>4s}: predicted={pred:.1%},"
                f" actual={actual:.1%} (n={n:.0f})"
            )
    print(f"{'=' * 50}\n")
