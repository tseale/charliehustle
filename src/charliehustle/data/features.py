"""Feature engineering for game prediction."""

import logging

import numpy as np
import pandas as pd

from charliehustle.config import DEFAULT_CONFIG, Config

logger = logging.getLogger(__name__)

FEATURE_COLUMNS = [
    "home_elo",
    "away_elo",
    "elo_home_prob",
    "home_win_pct",
    "away_win_pct",
    "home_run_diff",
    "away_run_diff",
    "home_pyth_win_pct",
    "away_pyth_win_pct",
    "home_rest_days",
    "away_rest_days",
]

TARGET_COLUMN = "home_win"


def compute_elo_ratings(
    games: pd.DataFrame,
    config: Config = DEFAULT_CONFIG,
) -> pd.DataFrame:
    """Compute pre-game ELO ratings for every game.

    Adds columns: home_elo, away_elo, elo_home_prob.
    """
    k = config.elo_k
    hfa = config.elo_home_advantage
    mean = config.elo_mean

    teams = set(games["home_team"]) | set(games["away_team"])
    elo: dict[str, float] = {team: mean for team in teams}

    home_elos: list[float] = []
    away_elos: list[float] = []
    home_probs: list[float] = []

    for _, game in games.iterrows():
        home, away = game["home_team"], game["away_team"]
        h_elo, a_elo = elo[home], elo[away]

        home_elos.append(h_elo)
        away_elos.append(a_elo)

        # Expected outcome with home-field advantage
        exp_home = 1 / (1 + 10 ** ((a_elo - h_elo - hfa) / 400))
        home_probs.append(exp_home)

        # Update ratings
        actual_home = float(game["home_win"])
        elo[home] = h_elo + k * (actual_home - exp_home)
        elo[away] = a_elo + k * ((1 - actual_home) - (1 - exp_home))

    games = games.copy()
    games["home_elo"] = home_elos
    games["away_elo"] = away_elos
    games["elo_home_prob"] = home_probs
    return games


def compute_team_rolling_stats(
    games: pd.DataFrame,
    window: int = 30,
) -> pd.DataFrame:
    """Compute rolling team stats and attach them as pre-game features.

    For each game, features represent team state BEFORE that game was played.
    """
    teams = set(games["home_team"]) | set(games["away_team"])
    team_logs: dict[str, list[dict]] = {t: [] for t in teams}

    # First pass: build per-team game logs in order
    for _, game in games.iterrows():
        home, away = game["home_team"], game["away_team"]
        team_logs[home].append(
            {
                "runs_scored": game["home_score"],
                "runs_allowed": game["away_score"],
                "won": game["home_win"],
            }
        )
        team_logs[away].append(
            {
                "runs_scored": game["away_score"],
                "runs_allowed": game["home_score"],
                "won": 1 - game["home_win"],
            }
        )

    # Second pass: compute features using history available before each game
    team_game_idx: dict[str, int] = {t: 0 for t in teams}
    team_histories: dict[str, list[dict]] = {t: [] for t in teams}

    features: dict[str, list] = {
        "home_win_pct": [],
        "away_win_pct": [],
        "home_run_diff": [],
        "away_run_diff": [],
        "home_pyth_win_pct": [],
        "away_pyth_win_pct": [],
        "home_games_played": [],
        "away_games_played": [],
    }

    for _, game in games.iterrows():
        home, away = game["home_team"], game["away_team"]

        for prefix, team in [("home", home), ("away", away)]:
            history = team_histories[team]
            n = len(history)

            if n == 0:
                features[f"{prefix}_win_pct"].append(0.5)
                features[f"{prefix}_run_diff"].append(0.0)
                features[f"{prefix}_pyth_win_pct"].append(0.5)
                features[f"{prefix}_games_played"].append(0)
            else:
                recent = history[-window:]
                wins = sum(g["won"] for g in recent)
                rs = sum(g["runs_scored"] for g in recent)
                ra = sum(g["runs_allowed"] for g in recent)

                features[f"{prefix}_win_pct"].append(wins / len(recent))
                features[f"{prefix}_run_diff"].append((rs - ra) / len(recent))

                # Pythagorean expected win% (exponent 1.83)
                if rs + ra > 0:
                    pyth = rs**1.83 / (rs**1.83 + ra**1.83)
                else:
                    pyth = 0.5
                features[f"{prefix}_pyth_win_pct"].append(pyth)
                features[f"{prefix}_games_played"].append(n)

            # Add this game to history AFTER computing features
            log = team_logs[team][team_game_idx[team]]
            team_histories[team].append(log)
            team_game_idx[team] += 1

    games = games.copy()
    for col, values in features.items():
        games[col] = values

    return games


def compute_rest_days(games: pd.DataFrame) -> pd.DataFrame:
    """Compute days of rest for each team before each game."""
    last_game_date: dict[str, pd.Timestamp] = {}
    home_rest: list[int] = []
    away_rest: list[int] = []

    for _, game in games.iterrows():
        home, away = game["home_team"], game["away_team"]
        game_date = game["date"]

        for rest_list, team in [(home_rest, home), (away_rest, away)]:
            if team in last_game_date:
                delta = (game_date - last_game_date[team]).days
                rest_list.append(min(delta, 7))  # Cap at 7 for all-star break etc.
            else:
                rest_list.append(3)  # Default for season opener
            last_game_date[team] = game_date

    games = games.copy()
    games["home_rest_days"] = home_rest
    games["away_rest_days"] = away_rest
    return games


def build_feature_matrix(
    games: pd.DataFrame,
    config: Config = DEFAULT_CONFIG,
) -> pd.DataFrame:
    """Build complete feature matrix from raw game data.

    Computes ELO ratings, rolling team stats, and rest days.
    Drops early-season games with insufficient history.
    """
    logger.info(f"Building features for {len(games)} games...")

    games = compute_elo_ratings(games, config)
    games = compute_team_rolling_stats(games, config.rolling_window)
    games = compute_rest_days(games)

    # Drop games where either team has played fewer than rolling_window games
    min_games = config.rolling_window
    games = games[
        (games["home_games_played"] >= min_games)
        & (games["away_games_played"] >= min_games)
    ].copy()

    logger.info(
        f"Feature matrix: {len(games)} games with {len(FEATURE_COLUMNS)} features"
    )
    return games
