"""Model prediction."""

import numpy as np
import pandas as pd
from xgboost import XGBClassifier

from charliehustle.data.features import FEATURE_COLUMNS


def predict_games(
    model: XGBClassifier,
    games: pd.DataFrame,
) -> pd.DataFrame:
    """Generate predictions for a set of games.

    Adds columns:
        model_home_prob: predicted probability of home win
        model_pick: predicted winner team name
    """
    X = games[FEATURE_COLUMNS].values
    probs = model.predict_proba(X)[:, 1]  # P(home_win)

    games = games.copy()
    games["model_home_prob"] = probs
    games["model_pick"] = np.where(
        probs >= 0.5, games["home_team"], games["away_team"]
    )
    return games
