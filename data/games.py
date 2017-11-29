import mlbgame
import datetime
import numpy as np
import pandas as pd

def games_for_date(month=None, day=None, year=None):
    if (month is None) or (day is None) or (year is None):
        raise ValueError
    games = [y for x in mlbgame.games(year, month, day) for y in x]
    data = pd.DataFrame({'game_id':[game.game_id for game in games],
                         'date':[game.date for game in games],
                         'away_team':[game.away_team for game in games],
                         'home_team':[game.home_team for game in games]})
    return data
