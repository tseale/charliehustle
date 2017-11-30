import mlbgame
import datetime
import numpy as np
import pandas as pd

#Public Methods
def data_for_games_today():
    return data_for_game_ids(game_ids_for_today())

def data_for_games_on_date(month=None, day=None, year=None):
    return data_for_game_ids(game_ids_for_date(month, day, year))




#Helper Methods
def game_ids_for_today():
    today = datetime.datetime.today()
    return game_ids_for_date(today.month, today.day, today.year)

def game_ids_for_date(month=None, day=None, year=None):
    if (month is None) or (day is None) or (year is None):
        raise ValueError('Month, Day, and Year must all be provided as arguments.')
    return [game.game_id for x in mlbgame.games(year, month, day) for game in x]

def data_for_game_ids(game_ids):
    data =[]
    for game_id in game_ids:
        game = mlbgame.overview(game_id)
        data.append({'away_team_id':game.away_team_id,
                     'home_team_id':game.home_team_id,
                     'away_team_win_pct':float(game.away_win)/(float(game.away_win)+float(game.away_loss)),
                     'home_team_win_pct':float(game.home_win)/(float(game.home_win)+float(game.home_loss)),
                     'winning_team':game.home_team_id if int(game.home_team_runs)>int(game.away_team_runs) else game.away_team_id})
    return pd.DataFrame(data)
