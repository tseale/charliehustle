import build
import simulate
import pick

import test

import pandas as pd
import numpy as np

#pickMethods = {'Pythagorean Win %':pick.based_on_pythagorean_expected_win_pct,
#               'Pythagorean Win % + HFA':pick.based_on_pythagorean_expected_win_pct_plus_home_team_advantage,
#               'Pre-ELO Rating':pick.based_on_pre_elo_rating,
#               'Pre-ELO Rating (Contrarian)':pick.based_on_pre_elo_rating_contrarian}

pickMethods = {'Model':pick.based_on_model}

#seasons = range(2010,2018)
data = build.data_for_seasons([2017])

#trainingData = pd.DataFrame()
#for season in range(2011,2017):
#    trainingData = trainingData.append(data[season].dropna())

#testData = data[2017].dropna()

#columns = ['AwayTeamPythagoreanExpectedWin%','HomeTeamPythagoreanExpectedWin%',
#           'AwayTeamRating','HomeTeamRating',
#           'AwayTeamStartingPitcherRating','HomeTeamStartingPitcherRating',
#           'AwayTeamLine','HomeTeamLine',
#           'WasHomeTeamWinner']

#testData = testData[columns]
#trainingData = trainingData[columns]

#print 'Test Data Shape: ' + str(testData.shape)
#print 'Training Data Shape: ' + str(trainingData.shape)

#testData.to_csv('data/test/mlb_test.csv', header=False, index=False)
#trainingData.to_csv('data/train/mlb_train.csv', header=False, index=False)

#test.main()
#print test.predict([0.67565872963,0.67565872963,1557.11137163,1508.33424545,52.1179250754,54.6351186533,-113,104])

simulate.with_data(data)
simulate.with_bankroll(1000)
simulate.with_methods(pickMethods)
simulate.games_for_seasons([2017])
