"""Data fetching from MLB Stats API and pybaseball."""

import logging

import pandas as pd
import statsapi

from charliehustle.config import DEFAULT_CONFIG, Config
from charliehustle.data.storage import load_parquet, save_parquet

logger = logging.getLogger(__name__)


def fetch_season_games(
    season: int, config: Config = DEFAULT_CONFIG
) -> pd.DataFrame:
    """Fetch all regular season games for a season from MLB Stats API.

    Returns a DataFrame with one row per completed regular-season game.
    """
    cache_path = config.data_dir / f"{season}" / "games.parquet"
    cached = load_parquet(cache_path)
    if cached is not None:
        logger.info(f"Loaded {len(cached)} games from cache for {season}")
        return cached

    logger.info(f"Fetching {season} schedule from MLB Stats API...")
    raw = statsapi.schedule(
        start_date=f"03/20/{season}",
        end_date=f"11/15/{season}",
        sportId=1,
    )

    records = []
    for g in raw:
        if g["game_type"] != "R":
            continue
        if g["status"] != "Final":
            continue
        records.append(
            {
                "game_id": g["game_id"],
                "date": g["game_date"],
                "home_team": g["home_name"],
                "home_id": g["home_id"],
                "away_team": g["away_name"],
                "away_id": g["away_id"],
                "home_score": g["home_score"],
                "away_score": g["away_score"],
                "home_win": int(g["home_score"] > g["away_score"]),
                "winning_pitcher": g.get("winning_pitcher", ""),
                "losing_pitcher": g.get("losing_pitcher", ""),
            }
        )

    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    save_parquet(df, cache_path)
    logger.info(f"Fetched and cached {len(df)} games for {season}")
    return df


def fetch_pitching_stats(
    season: int, config: Config = DEFAULT_CONFIG
) -> pd.DataFrame:
    """Fetch season pitching stats from FanGraphs via pybaseball."""
    from pybaseball import pitching_stats

    cache_path = config.data_dir / f"{season}" / "pitching_stats.parquet"
    cached = load_parquet(cache_path)
    if cached is not None:
        return cached

    logger.info(f"Fetching {season} pitching stats from FanGraphs...")
    df = pitching_stats(season, qual=0)

    save_parquet(df, cache_path)
    return df


def fetch_batting_stats(
    season: int, config: Config = DEFAULT_CONFIG
) -> pd.DataFrame:
    """Fetch season batting stats from FanGraphs via pybaseball."""
    from pybaseball import batting_stats

    cache_path = config.data_dir / f"{season}" / "batting_stats.parquet"
    cached = load_parquet(cache_path)
    if cached is not None:
        return cached

    logger.info(f"Fetching {season} batting stats from FanGraphs...")
    df = batting_stats(season, qual=0)

    save_parquet(df, cache_path)
    return df
