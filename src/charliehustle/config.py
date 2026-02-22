"""Configuration for charliehustle."""

from pathlib import Path

from pydantic import BaseModel


class Config(BaseModel):
    """Global configuration."""

    data_dir: Path = Path("data")

    # ELO settings
    elo_k: float = 4.0
    elo_home_advantage: float = 24.0
    elo_mean: float = 1500.0
    elo_reversion_factor: float = 1 / 3

    # Feature engineering
    rolling_window: int = 30

    # Betting
    initial_bankroll: float = 1000.0
    kelly_fraction: float = 0.25
    min_edge: float = 0.02
    max_bet_fraction: float = 0.05


DEFAULT_CONFIG = Config()
