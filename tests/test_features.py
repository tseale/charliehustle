"""Tests for feature engineering."""

import pandas as pd
import pytest

from charliehustle.config import Config
from charliehustle.data.features import (
    compute_elo_ratings,
    compute_rest_days,
    compute_team_rolling_stats,
)


def _make_games(n: int = 10) -> pd.DataFrame:
    """Create a minimal games DataFrame for testing."""
    records = []
    for i in range(n):
        home_win = i % 2
        records.append(
            {
                "game_id": i,
                "date": pd.Timestamp(f"2024-04-{i + 1:02d}"),
                "home_team": "Team A",
                "away_team": "Team B",
                "home_id": 1,
                "away_id": 2,
                "home_score": 5 if home_win else 3,
                "away_score": 3 if home_win else 5,
                "home_win": home_win,
            }
        )
    return pd.DataFrame(records)


class TestEloRatings:
    def test_initial_ratings_are_mean(self):
        games = _make_games(1)
        result = compute_elo_ratings(games)
        assert result["home_elo"].iloc[0] == 1500.0
        assert result["away_elo"].iloc[0] == 1500.0

    def test_ratings_update_after_games(self):
        games = _make_games(2)
        result = compute_elo_ratings(games)
        # Game 0: home_win=0 (home loses), so home ELO should drop
        assert result["home_elo"].iloc[1] < 1500.0

    def test_elo_prob_in_valid_range(self):
        games = _make_games(20)
        result = compute_elo_ratings(games)
        assert (result["elo_home_prob"] >= 0).all()
        assert (result["elo_home_prob"] <= 1).all()

    def test_custom_config(self):
        games = _make_games(5)
        config = Config(elo_k=10.0, elo_home_advantage=0.0)
        result = compute_elo_ratings(games, config)
        # With no home advantage and k=10, ratings should change faster
        delta = abs(result["home_elo"].iloc[1] - 1500.0)
        assert delta > 1.0


class TestRollingStats:
    def test_first_game_defaults(self):
        games = _make_games(1)
        result = compute_team_rolling_stats(games, window=30)
        assert result["home_win_pct"].iloc[0] == 0.5
        assert result["away_win_pct"].iloc[0] == 0.5
        assert result["home_games_played"].iloc[0] == 0

    def test_stats_accumulate(self):
        games = _make_games(5)
        result = compute_team_rolling_stats(games, window=30)
        # After a few games, games_played should increase
        assert result["home_games_played"].iloc[4] == 4

    def test_pyth_win_pct_in_range(self):
        games = _make_games(10)
        result = compute_team_rolling_stats(games, window=30)
        # Skip first row (default 0.5)
        for col in ["home_pyth_win_pct", "away_pyth_win_pct"]:
            assert (result[col] >= 0).all()
            assert (result[col] <= 1).all()


class TestRestDays:
    def test_first_game_default(self):
        games = _make_games(1)
        result = compute_rest_days(games)
        assert result["home_rest_days"].iloc[0] == 3
        assert result["away_rest_days"].iloc[0] == 3

    def test_consecutive_days(self):
        games = _make_games(3)
        result = compute_rest_days(games)
        assert result["home_rest_days"].iloc[1] == 1

    def test_rest_capped_at_seven(self):
        records = [
            {
                "game_id": 0,
                "date": pd.Timestamp("2024-04-01"),
                "home_team": "A",
                "away_team": "B",
                "home_score": 5,
                "away_score": 3,
                "home_win": 1,
            },
            {
                "game_id": 1,
                "date": pd.Timestamp("2024-04-20"),  # 19 days later
                "home_team": "A",
                "away_team": "B",
                "home_score": 3,
                "away_score": 5,
                "home_win": 0,
            },
        ]
        games = pd.DataFrame(records)
        result = compute_rest_days(games)
        assert result["home_rest_days"].iloc[1] == 7
