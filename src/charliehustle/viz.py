"""Visualization utilities."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_bankroll(
    results: pd.DataFrame,
    title: str = "Bankroll Over Time",
    output_path: Path | None = None,
) -> None:
    """Plot bankroll trajectory from backtest results."""
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(range(len(results)), results["bankroll"], linewidth=1.5)
    ax.axhline(
        y=results["bankroll"].iloc[0],
        color="gray",
        linestyle="--",
        alpha=0.5,
        label="Starting bankroll",
    )

    ax.set_title(title)
    ax.set_xlabel("Bets Placed")
    ax.set_ylabel("Bankroll ($)")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=150)
        print(f"Saved plot to {output_path}")
    else:
        plt.show()
    plt.close(fig)


def plot_calibration(
    games: pd.DataFrame,
    n_bins: int = 10,
    output_path: Path | None = None,
) -> None:
    """Plot calibration curve: predicted vs actual win probability."""
    fig, ax = plt.subplots(figsize=(8, 8))

    probs = games["model_home_prob"].values
    actual = games["home_win"].values

    bin_edges = np.linspace(0, 1, n_bins + 1)
    bin_centers = []
    bin_actuals = []

    for i in range(n_bins):
        mask = (probs >= bin_edges[i]) & (probs < bin_edges[i + 1])
        if mask.sum() > 0:
            bin_centers.append(probs[mask].mean())
            bin_actuals.append(actual[mask].mean())

    ax.plot([0, 1], [0, 1], "k--", alpha=0.5, label="Perfect calibration")
    ax.scatter(bin_centers, bin_actuals, s=80, zorder=5)
    ax.plot(bin_centers, bin_actuals, linewidth=1.5, label="Model")

    ax.set_title("Calibration Curve")
    ax.set_xlabel("Predicted Probability (Home Win)")
    ax.set_ylabel("Actual Probability (Home Win)")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=150)
        print(f"Saved plot to {output_path}")
    else:
        plt.show()
    plt.close(fig)
