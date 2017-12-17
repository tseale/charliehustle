import test
import math

def convert_line_to_win_prob(line):
    if float(line)>0:
        return 100./(float(line)+100.)
    else:
        return float(line)/(float(line)-100.)

def convert_win_prob_to_line(prob):
    prob *= 100.
    if float(prob)>50:
        return int((prob/(100.-prob))*-100.)
    else:
        return int(((100.-prob)/prob)*100.)

def has_underdog_advantage(line,modelLine):
    return (float(modelLine)-float(line))>20

def based_on_model(game):
    columns = ['AwayTeamPythagoreanExpectedWin%','HomeTeamPythagoreanExpectedWin%',
               'AwayTeamRating','HomeTeamRating',
               'AwayTeamStartingPitcherRating','HomeTeamStartingPitcherRating',
               'AwayTeamLine','HomeTeamLine']
    data = game[columns]
    modelPick = test.predict(list(data))
    wasHomeTeamWinner = modelPick[0]
    pick = game['HomeTeam'] if modelPick[0]==0 else game['AwayTeam']
    confidence = 0.01
    if not math.isnan(float(modelPick[1])) and not math.isnan(float(modelPick[1])):
        awayTeamModelLine = convert_win_prob_to_line(modelPick[1])
        homeTeamModelLine = convert_win_prob_to_line(modelPick[2])
    else:
        awayTeamModelLine = None
        homeTeamModelLine = None
    if awayTeamModelLine and homeTeamModelLine:
        isHomeTeamUnderdog = game['HomeTeamLine']>game['AwayTeamLine']
        underdogTeam = game['HomeTeam'] if isHomeTeamUnderdog else game['AwayTeam']
        underdogLine = game['HomeTeamLine'] if isHomeTeamUnderdog else game['AwayTeamLine']
        underdogModelLine = homeTeamModelLine if isHomeTeamUnderdog else awayTeamModelLine
        if has_underdog_advantage(underdogLine,underdogModelLine):
            isPickUnderdog = 1 if pick==underdogLine else 0
            if not isPickUnderdog:
                pick = underdogTeam
    return pick,confidence

def based_on_pre_elo_rating(game):
    pick = game['HomeTeam'] if game['HomePreELO']>=game['AwayPreELO'] else game['AwayTeam']
    confidence = 0.01
    return pick,confidence

def based_on_pre_elo_rating_contrarian(game):
    pick = game['HomeTeam'] if game['HomePreELO']<=game['AwayPreELO'] else game['AwayTeam']
    confidence = 0.01
    return pick,confidence

def based_on_pythagorean_expected_win_pct(game):
    pick = game['HomeTeam'] if game['HomeExpWin%']>=game['AwayExpWin%'] else game['AwayTeam']
    confidence = 0.01
    return pick,confidence

def based_on_pythagorean_expected_win_pct_plus_home_team_advantage(game):
    adjAwayExpWinPct = game['AwayExpWin%'] + 0.04
    adjHomeExpWinPct = game['HomeExpWin%'] - 0.04
    pick = game['HomeTeam'] if adjHomeExpWinPct>=adjAwayExpWinPct else game['AwayTeam']
    confidence = 0.01
    return pick,confidence
