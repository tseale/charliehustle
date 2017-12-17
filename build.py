import numpy as np
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import json
import os

import mlbgame

eloData = None

teamAbbrevs = ['ARI','ATL','BAL','BOS','CHC','CWS','CIN','CLE','COL',
               'DET','HOU','KC','LAA','LAD','MIA','MIL','MIN','NYM',
               'NYY','OAK','PHI','PIT','SD','SEA','SF','STL','TB',
               'TEX','TOR','WSH']

mlbgameTeamAbbrevToCoversTeamID = {'ARI':2968,'ATL':2957,'BAL':2959,'BOS':2966,
                                    'CHC':2982,'CWS':2974,'CIN':2961,'CLE':2980,
                                    'COL':2956,'DET':2978,'HOU':2981,'KC':2965,
                                    'LAA':2979,'LAD':2967,'MIA':2963,'MIL':2976,
                                    'MIN':2983,'NYM':2964,'NYY':2970,'OAK':2969,
                                    'PHI':2958,'PIT':2971,'SD':2955,'SEA':2973,
                                    'SF':2962,'STL':2975,'TB':2960,'TEX':2977,
                                    'TOR':2984,'WSH':2972}

mlbgameTeamAbbrevTo538TeamAbbrev = {'ARI':'ARI','ATL':'ATL','BAL':'BAL','BOS':'BOS',
                                    'CHC':'CHC','CWS':'CHW','CIN':'CIN','CLE':'CLE',
                                    'COL':'COL','DET':'DET','HOU':'HOU','KC':'KCR',
                                    'LAA':'ANA','LAD':'LAD','MIA':'FLA','MIL':'MIL',
                                    'MIN':'MIN','NYM':'NYM','NYY':'NYY','OAK':'OAK',
                                    'PHI':'PHI','PIT':'PIT','SD':'SDP','SEA':'SEA',
                                    'SF':'SFG','STL':'STL','TB':'TBD','TEX':'TEX',
                                    'TOR':'TOR','WSH':'WSN'}

def data_for_seasons(seasons):
    data = {}
    for season in seasons:
        teams_data_for_season(season)
        data[season] = games_data_for_season(season)
    return data

# Games Data Building Methods
def games_data_for_season(season):
    data = {}
    filePath = 'data/{}/games/'.format(season)
    if not os.path.exists(filePath):
        os.makedirs(filePath)
    gamesFile = 'data/{}/games/{}_games_data.csv'.format(season,season)
    if not os.path.exists(gamesFile):
        games_in_season(season)
    data = pd.read_csv(gamesFile)
    return data

def games_in_season(season):
    print 'Building data/{}/games/{}_games_data.csv'.format(season,season)
    dataList = []
    for month in range(4,12):
        for day in range(1,32):
            print '\n{}/{}/{}'.format(month,day,season)
            for gameID in game_ids_for_date(month,day,season):
                try:
                    game = mlbgame.overview(gameID)
                except:
                    break
                if not data_exists_for_game(game):
                    break
                awayData = pd.read_csv('data/{}/teams/{}_{}_data.csv'.format(season,game.away_name_abbrev,season))
                homeData = pd.read_csv('data/{}/teams/{}_{}_data.csv'.format(season,game.home_name_abbrev,season))
                gameData = (awayData,homeData)
                if not hasattr(game,'time_date'):
                    break
                if not game_dates_match(game.time_date,gameData):
                    break
                gameNumber = game_number_for_game(game)
                lines = line_for_game(gameData,gameNumber)
                overUnder = over_under_for_game(gameData,gameNumber)
                print game.away_name_abbrev,'@',game.home_name_abbrev
                teamRatings = team_rating_for_game(gameData,gameNumber)
                expWinPcts = pythagorean_win_pct_for_game(gameData,gameNumber)
                startingPitcherRatings = starting_pitcher_rating_for_game(gameData,gameNumber)
                startingPitcherAdjustments = starting_pitcher_adjustment_for_game(gameData,gameNumber)
                teamWinProbabilities = win_probability_for_game(gameData,gameNumber)
                winningTeam = game.home_name_abbrev if int(game.home_team_runs)>int(game.away_team_runs) else game.away_name_abbrev
                winningLine = lines[1] if winningTeam==game.home_name_abbrev else lines[0]
                wasHomeTeamWinner = 1 if winningTeam==game.home_name_abbrev else 0
                dataList.append({'Date':game.time_date,
                                 'AwayTeam':game.away_name_abbrev,
                                 'HomeTeam':game.home_name_abbrev,
                                 'AwayTeamID':mlbgameTeamAbbrevToCoversTeamID[game.away_name_abbrev],
                                 'HomeTeamID':mlbgameTeamAbbrevToCoversTeamID[game.home_name_abbrev],
                                 'AwayTeamStartingPitcherRating':startingPitcherRatings[0],
                                 'HomeTeamStartingPitcherRating':startingPitcherRatings[1],
                                 'AwayTeamStartingPitcherAdjustment':startingPitcherAdjustments[0],
                                 'HomeTeamStartingPitcherAdjustment':startingPitcherAdjustments[1],
                                 'AwayTeamWinProbability':teamWinProbabilities[0],
                                 'HomeTeamWinProbability':teamWinProbabilities[1],
                                 'WinningTeam':winningTeam,
                                 'WinningTeamID':mlbgameTeamAbbrevToCoversTeamID[winningTeam],
                                 'WasHomeTeamWinner':wasHomeTeamWinner,
                                 'AwayTeamLine':lines[0],
                                 'HomeTeamLine':lines[1],
                                 'Over/Under':overUnder,
                                 'WinningTeamLine':winningLine,
                                 'AwayTeamRating':teamRatings[0],
                                 'HomeTeamRating':teamRatings[1],
                                 'AwayTeamPythagoreanExpectedWin%':expWinPcts[0],
                                 'HomeTeamPythagoreanExpectedWin%':expWinPcts[1]})
    data = pd.DataFrame(dataList)
    data.to_csv('data/{}/games/{}_games_data.csv'.format(season,season), encoding='utf-8')

def game_ids_for_date(month=None, day=None, year=None):
    if (month is None) or (day is None) or (year is None):
        raise ValueError('Month, Day, and Year must all be provided as arguments.')
    return [game.game_id for x in mlbgame.games(year, month, day) for game in x]

def data_exists_for_game(game):
    if game.away_name_abbrev in teamAbbrevs and game.home_name_abbrev in teamAbbrevs:
        if hasattr(game,'away_team_runs') and hasattr(game,'home_team_runs'):
            return True
    return False

def game_dates_match(date,gameData):
    gameDate = datetime.strptime(date, '%Y/%m/%d %H:%M').strftime('%Y/%m/%d')
    if any(gameDate in s for s in gameData[0]['Date'].tolist()) and any(gameDate in s for s in gameData[1]['Date'].tolist()):
        return True
    return False

def game_number_for_game(game):
    awayTeamGameNumber = int(game.away_win)+int(game.away_loss)-1
    homeTeamGameNumber = int(game.home_win)+int(game.home_loss)-1
    return awayTeamGameNumber,homeTeamGameNumber

def line_for_game(gameData,gameNumber):
    awayTeamLine = gameData[0].iloc[gameNumber[0]]['Line']
    homeTeamLine = gameData[1].iloc[gameNumber[1]]['Line']
    return awayTeamLine,homeTeamLine

def over_under_for_game(gameData,gameNumber):
    awayTeamOverUnder = gameData[0].iloc[gameNumber[0]]['Over/Under']
    homeTeamOverUnder= gameData[1].iloc[gameNumber[1]]['Over/Under']
    if int(awayTeamOverUnder) is not int(homeTeamOverUnder):
        return None
    return homeTeamOverUnder

def team_rating_for_game(gameData,gameNumber):
    awayTeamRating = gameData[0].iloc[gameNumber[0]]['TeamRating']
    homeTeamRating = gameData[1].iloc[gameNumber[1]]['TeamRating']
    return awayTeamRating,homeTeamRating

def starting_pitcher_adjustment_for_game(gameData,gameNumber):
    awayTeamStartingPitcherAdjustment = gameData[0].iloc[gameNumber[0]]['StartingPitcherAdjustment']
    homeTeamStartingPitcherAdjustment = gameData[1].iloc[gameNumber[1]]['StartingPitcherAdjustment']
    return awayTeamStartingPitcherAdjustment,homeTeamStartingPitcherAdjustment

def starting_pitcher_rating_for_game(gameData,gameNumber):
    awayTeamStartingPitcherRating = gameData[0].iloc[gameNumber[0]]['StartingPitcherRating']
    homeTeamStartingPitcherRating = gameData[1].iloc[gameNumber[1]]['StartingPitcherRating']
    return awayTeamStartingPitcherRating,homeTeamStartingPitcherRating

def pythagorean_win_pct_for_game(gameData,gameNumber):
    awayTeamPythagoreanWinPct = gameData[0].iloc[gameNumber[0]]['PythagoreanExpectedWin%']
    homeTeamPythagoreanWinPct = gameData[1].iloc[gameNumber[1]]['PythagoreanExpectedWin%']
    return awayTeamPythagoreanWinPct,homeTeamPythagoreanWinPct

def win_probability_for_game(gameData,gameNumber):
    awayTeamWinProbability = gameData[0].iloc[gameNumber[0]]['WinProbability']
    homeTeamWinProbability = gameData[1].iloc[gameNumber[1]]['WinProbability']
    return awayTeamWinProbability,homeTeamWinProbability

# Teams Data Building Methods
def teams_data_for_season(season):
    global eloData,mlbgameTeamAbbrevToCoversTeamID
    eloData = pd.read_csv('data/mlb_elo.csv')
    for team in mlbgameTeamAbbrevToCoversTeamID:
        filePath = 'data/{}/teams/'.format(season)
        if not os.path.exists(filePath):
            os.makedirs(filePath)
        teamFile = 'data/{}/teams/{}_{}_data.csv'.format(season,team,season)
        if not os.path.exists(teamFile):
            team_data_for_season(team,season)

def team_data_for_season(team,season):
    global eloData
    print 'Building data/{}/teams/{}_{}_data.csv'.format(season,team,season)
    dataList = []
    url = 'https://www.covers.com/pageLoader/pageLoader.aspx?page=/data/mlb/teams/pastresults/{}/team{}.html'
    url = url.format(season,mlbgameTeamAbbrevToCoversTeamID[team])
    s=requests.get(url).content
    soup = BeautifulSoup(s, 'html.parser')
    content = soup.find(id='content')
    tables = content.find_all('table')
    table = tables[1] if len(tables)>1 else tables[0]
    rows = table.find_all('tr')
    teamEloData = eloData[np.logical_and(np.logical_or(eloData['team1']==mlbgameTeamAbbrevTo538TeamAbbrev[team],eloData['team2']==mlbgameTeamAbbrevTo538TeamAbbrev[team]),eloData['season']==season)]
    for i,row in enumerate(reversed(rows[1:])):
        cols = [ele.text.strip() for ele in row.find_all('td')]
        # format column data nicely
        date = datetime.strptime(str(cols[0]),'%m/%d/%y').strftime('%Y/%m/%d')
        homeAway = 'A' if '@' in str(cols[1]) else 'H'
        opp = str(cols[1]).replace('@','').strip()
        winLoss = 1 if 'W' in str(cols[2]) else 0
        score = str(cols[2]).replace('W','').replace('L','').strip().split('-')
        runs = int(score[0]) if winLoss==1 else int(score[1])
        runsAllowed = int(score[1]) if winLoss==1 else int(score[0])
        line = str(cols[5])[1:].strip()
        overUnder = str(cols[6])[1:].strip().split(' ')[0].strip()
        # FiveThirtyEight MLB Data
        teamRating = teamEloData.iloc[i]['rating1_pre'] if homeAway=='H' else teamEloData.iloc[i]['rating2_pre']
        startingPitcherKey = teamEloData.iloc[i]['pitcher1'] if homeAway=='H' else teamEloData.iloc[i]['pitcher2']
        startingPitcherRating = teamEloData.iloc[i]['pitcher1_rating'] if homeAway=='H' else teamEloData.iloc[i]['pitcher2_rating']
        startingPitcherAdjustment = teamEloData.iloc[i]['pitcher1_adj'] if homeAway=='H' else teamEloData.iloc[i]['pitcher2_adj']
        winProbability = teamEloData.iloc[i]['rating_prob1'] if homeAway=='H' else teamEloData.iloc[i]['rating_prob2']
        # add columns to data in dictionary
        dataList.append({'Date':date,
                         'TeamRating':teamRating,
                         'Home/Away':homeAway,
                         'Opponent':opp,
                         'Win/Loss':winLoss,
                         'Runs':runs,
                         'RunsAllowed':runsAllowed,
                         'StartingPitcherKey':startingPitcherKey,
                         'StartingPitcherRating':startingPitcherRating,
                         'StartingPitcherAdjustment':startingPitcherAdjustment,
                         'WinProbability':winProbability,
                         'Line':line,
                         'Over/Under':overUnder})
    data = pd.DataFrame(dataList)
    data['TotalRunsScored'] = data['Runs'].cumsum()
    data['TotalRunsAllowed'] = data['RunsAllowed'].cumsum()
    data['Wins'] = np.where(data['Win/Loss']==1, 1, 0).cumsum()
    data['Loses'] = np.where(data['Win/Loss']==0, 1, 0).cumsum()
    data['Win%'] = data['Wins']/(data['Wins']+data['Loses'])
    data['PythagoreanExpectedWin%'] = np.power(data['TotalRunsScored'],1.81)/(np.power(data['TotalRunsScored'],1.81)+np.power(data['TotalRunsAllowed'],1.81))
    data['PythagoreanExpectedWin%'] = data['PythagoreanExpectedWin%'].shift(1)
    data.to_csv('data/{}/teams/{}_{}_data.csv'.format(season,team,season), encoding='utf-8')
