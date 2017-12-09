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
