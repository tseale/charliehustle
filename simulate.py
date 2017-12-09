import mlbgame
import datetime
import numpy as np
import pandas as pd
import math

import matplotlib.pyplot as plt

simulationData = {}
pickMethods = {}
initialBankroll = 0.0
bankrollTrend = {}

# Setup Methods
def with_bankroll(amount):
    global initialBankroll
    initialBankroll = amount

def with_data(data):
    global simulationData
    simulationData = data

def with_methods(methods):
    global pickMethods,initialBankroll
    pickMethods = methods
    for key in pickMethods.keys():
        bankrollTrend[key] = [initialBankroll]

#Public Methods
def games_for_seasons(seasons):
    global simulationData,pickMethod,bankrollTrend
    for season in seasons:
        seasonData = simulationData[season]
        for i,row in seasonData.iterrows():
            game = seasonData.iloc[i]
            for key,method in pickMethods.items():
                pick,confidence = method(game)
                pickLine = game['HomeLine'] if pick==game['HomeTeam'] else game['AwayLine']

                bankroll = bankrollTrend[key][-1]
                betAmount = round(float(bankroll)*confidence,2)
                bankroll -= betAmount

                didWinPick = (pick==game['WinningTeam'])
                if didWinPick:
                    winningsAmount = round(float(betAmount)*float(convert_line_to_multiplier(game['WinningLine'])),2)
                    bankroll += winningsAmount
                bankrollTrend[key].append(bankroll)

        plt.title(str(season) + ' MLB Season' );
        plt.xlabel('Games Bet')
        plt.ylabel('Bankroll ($)')
        for label,trend in bankrollTrend.items():
            plt.plot(trend, label=label)
        plt.legend(loc=0)
        plt.savefig('graphs/mlb_{}.png'.format(season))

def convert_line_to_multiplier(line):
    if float(line)>0:
        return float(line)/100.0 + 1.0
    return 100.0/float(abs(line)) + 1.0
