"""Data caching and storage utilities."""

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def save_parquet(df: pd.DataFrame, path: Path) -> None:
    """Save a DataFrame as Parquet."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    logger.debug(f"Saved {len(df)} rows to {path}")


def load_parquet(path: Path) -> pd.DataFrame | None:
    """Load a Parquet file, returning None if it doesn't exist."""
    if path.exists():
        return pd.read_parquet(path)
    return None
