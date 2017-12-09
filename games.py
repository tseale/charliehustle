import mlbgame
from pybaseball import schedule_and_record
import datetime
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests

# Global Variable
teamScheduleAndRecordData = {}
totalWinningPicks = 0
totalPicks = 0

bankroll = 1000
bankrollTrend = []

mlbgameTeamAbbrevToBbrefTeamAbbrev = {'ARI':'ARI','ATL':'ATL','BAL':'BAL','BOS':'BOS',
                                      'CHC':'CHC','CWS':'CHW','CIN':'CIN','CLE':'CLE',
                                      'COL':'COL','DET':'DET','HOU':'HOU','KC':'KCR',
                                      'LAA':'LAA','LAD':'LAD','MIA':'MIA','MIL':'MIL',
                                      'MIN':'MIN','NYM':'NYM','NYY':'NYY','OAK':'OAK',
                                      'PHI':'PHI','PIT':'PIT','SD':'SDP','SEA':'SEA',
                                      'SF':'SFG','STL':'STL','TB':'TBR','TEX':'TEX',
                                      'TOR':'TOR','WSH':'WSN'}

mlbgameTeamAbbrevToCoversTeamID = {'ARI':2968,'ATL':2957,'BAL':2959,'BOS':2966,
                                    'CHC':2982,'CWS':2974,'CIN':2961,'CLE':2980,
                                    'COL':2956,'DET':2978,'HOU':2981,'KC':2965,
                                    'LAA':2979,'LAD':2967,'MIA':2963,'MIL':2976,
                                    'MIN':2983,'NYM':2964,'NYY':2970,'OAK':2969,
                                    'PHI':2958,'PIT':2971,'SD':2955,'SEA':2973,
                                    'SF':2962,'STL':2975,'TB':2960,'TEX':2977,
                                    'TOR':2984,'WSH':2972}

#Public Methods
def data_for_games_in_season(year=None):
    print '\n' + str(year) + ' MLB'
    print '--------\n'
    global teamScheduleAndRecordData, totalWinningPicks, totalPicks, bankroll,bankrollTrend
    bankrollTrend = []
    teamScheduleAndRecordData = {}
    totalWinningPicks = 0
    totalPicks = 0
    seasonData = pd.DataFrame()
    for month in range(4,12):
        monthData = data_for_games_in_month(month, year)
        if not monthData is None and not monthData.empty:
            season_data.append(month_data, ignore_index=True)
    pickWinPercentage = math.ceil((float(totalWinningPicks)/float(totalPicks))*100)
    print '\n' + str(year) + ' Record: ' + str(totalWinningPicks) + '-' + str(totalPicks) + ' = ' + str(pickWinPercentage) + '%'
    print 'Bankroll: ' + '$' + str(bankroll)

    bankrollData = pd.DataFrame(bankrollTrend, columns=['bankroll'])
    plt.plot(bankrollData['bankroll'], label='')
    plt.xlabel('Games Bet')
    plt.ylabel('Bankroll ($)')
    plt.title(str(year) + ' MLB Season' );
    #plt.show()
    return seasonData

def data_for_games_in_month(month=None, year=None):
    monthData = pd.DataFrame()
    monthlyWinningPicks = 0
    monthlyTotalPicks = 0
    for day in range(1,32):
        dayData = data_for_games_on_date(month, day, year)
        if not dayData is None and not dayData.empty:
            monthlyWinningPicks += sum(dayData['pick_match'])
            monthlyTotalPicks += dayData.shape[0]
            monthData.append(dayData, ignore_index=True)
    monthlyPickWinPercentage = math.ceil((float(monthlyWinningPicks)/float(monthlyTotalPicks))*100)
    print datetime.date(year, month, 1).strftime('%B') + ' ' + str(year) + ': ' + str(monthlyWinningPicks) + '-' + str(monthlyTotalPicks) + ' = ' + str(monthlyPickWinPercentage) + '%' + ' ($' + str(bankroll) + ')'
    return monthData

def data_for_games_on_date(month=None, day=None, year=None):
    global totalWinningPicks, totalPicks
    build_team_schedule_and_record_data_for_season(year)
    data = data_for_game_ids(game_ids_for_date(month, day, year))
    if not data is None and not data.empty:
        totalWinningPicks += sum(data['pick_match'])
        totalPicks += data.shape[0]
        return data

def data_for_games_today():
    return data_for_game_ids(game_ids_for_today())

#Helper Methods
def build_team_schedule_and_record_data_for_season(year):
    global teamScheduleAndRecordData, mlbgameTeamAbbrevToBbrefTeamAbbrev
    if not teamScheduleAndRecordData:
        for team in mlbgameTeamAbbrevToBbrefTeamAbbrev:
            data = schedule_and_record(year, mlbgameTeamAbbrevToBbrefTeamAbbrev[team])
            data['total_runs_scored'] = data['R'].cumsum()
            data['total_runs_against'] = data['RA'].cumsum()
            data['pythagorean_exp_win_pct'] = np.power(data['total_runs_scored'],1.81)/(np.power(data['total_runs_scored'],1.81)+np.power(data['total_runs_against'],1.81))
            teamScheduleAndRecordData[team] = data
    return teamScheduleAndRecordData

def get_line_for_game(team,date):
    season = date[0:4]
    date = datetime.datetime.strptime(date, '%Y/%m/%d %H:%M').strftime('%m/%d/%y')
    url = 'https://www.covers.com/pageLoader/pageLoader.aspx?page=/data/mlb/teams/pastresults/{}/team{}.html'
    url = url.format(season,mlbgameTeamAbbrevToCoversTeamID[team])
    s=requests.get(url).content
    soup = BeautifulSoup(s, 'html.parser')
    content = soup.find(id='content')
    tables = content.find_all('table')
    for table in tables:
        rows = table.find_all('tr')
        for row in rows[1:]:
            cols = row.find_all('td')
            cols = [ele.text.replace('W','').replace('L','').strip() for ele in cols]
            if cols[0]==date:
                return float(cols[5])

def convert_line_to_multiplier(line):
    if line>0:
        return line*0.01 + 1
    return abs(line)*0.01

def data_for_game_ids(gameIDs):
    gamesData =[]
    global bankroll, bankrollTrend
    betAmount = math.ceil(bankroll * 0.01)
    for gameID in gameIDs:
        try:
            game = mlbgame.overview(gameID)
        except:
            break
        if does_data_exist_for_game(game):
            awayTeamLine = get_line_for_game(game.away_name_abbrev,game.time_date)
            homeTeamLine = get_line_for_game(game.home_name_abbrev,game.time_date)
            if awayTeamLine and homeTeamLine:
                bankrollTrend.append(bankroll)
                if bankroll<betAmount:
                    raise ValueError("Bankroll must be higher than bet amount")
                bankroll -= betAmount
                awayTeamWinProbability,homeTeamWinProbability = expected_win_probabilities_for_game(game)
                pick = game.home_name_abbrev if homeTeamWinProbability>=awayTeamWinProbability else game.away_name_abbrev
                winningTeam = game.home_name_abbrev if int(game.home_team_runs)>int(game.away_team_runs) else game.away_name_abbrev
                winningLine = homeTeamLine if winningTeam==game.home_name_abbrev else awayTeamLine

                gameDict = {'date':game.time_date,
                            'matchup':game.away_name_abbrev + ' @ ' + game.home_name_abbrev,
                            'away_team_win_pct':float(game.away_win)/(float(game.away_win)+float(game.away_loss)),
                            'home_team_win_pct':float(game.home_win)/(float(game.home_win)+float(game.home_loss)),
                            'pick':pick,
                            'away_team_line':awayTeamLine,
                            'home_team_line':awayTeamLine,
                            'winning_team':winningTeam,
                            'winning_line':winningLine}
                gamesData.append(gameDict)

                if pick==winningTeam:
                    bankroll += math.ceil(betAmount * convert_line_to_multiplier(winningLine))
                    print gameDict['date'],gameDict['matchup'],gameDict['pick'],gameDict['winning_line']

    if len(gamesData)>0:
        data = pd.DataFrame(gamesData)
        data['pick_match'] = np.where(data['pick']==data['winning_team'],1,0)
        return data

def does_data_exist_for_game(game):
    global mlbgameTeamAbbrevToBbrefTeamAbbrev
    if game.away_name_abbrev in mlbgameTeamAbbrevToBbrefTeamAbbrev and game.home_name_abbrev in mlbgameTeamAbbrevToBbrefTeamAbbrev:
        if hasattr(game,'away_team_runs') and hasattr(game,'home_team_runs'):
            return True
    return False

def expected_win_probabilities_for_game(game):
    awayTeamData = teamScheduleAndRecordData[game.away_name_abbrev]
    awayTeamGamesPlayed = int(game.away_win)+int(game.away_loss)-1
    homeTeamData = teamScheduleAndRecordData[game.home_name_abbrev]
    homeTeamGamesPlayed = int(game.home_win)+int(game.home_loss)-1

    awayTeamExpectedWinPct = awayTeamData.iloc[awayTeamGamesPlayed]['pythagorean_exp_win_pct']
    homeTeamExpectedWinPct = homeTeamData.iloc[homeTeamGamesPlayed]['pythagorean_exp_win_pct']

    awayTeamExpectedWinPct -= 0.04
    homeTeamExpectedWinPct += 0.04

    awayTeamWinProbability = awayTeamExpectedWinPct * (1.0-homeTeamExpectedWinPct)
    homeTeamWinProbability = homeTeamExpectedWinPct * (1.0-awayTeamExpectedWinPct)

    return awayTeamWinProbability,homeTeamWinProbability

def game_ids_for_date(month=None, day=None, year=None):
    if (month is None) or (day is None) or (year is None):
        raise ValueError('Month, Day, and Year must all be provided as arguments.')
    return [game.game_id for x in mlbgame.games(year, month, day) for game in x]

def game_ids_for_today():
    today = datetime.datetime.today()
    return game_ids_for_date(today.month, today.day, today.year)
