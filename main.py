import build
import simulate
import pick

pickMethods = {'Pythagorean Win %':pick.based_on_pythagorean_expected_win_pct,
               'Pythagorean Win % + HFA':pick.based_on_pythagorean_expected_win_pct_plus_home_team_advantage,
               'Pre-ELO Rating':pick.based_on_pre_elo_rating,
               'Pre-ELO Rating (Contrarian)':pick.based_on_pre_elo_rating_contrarian}

seasons = range(2017,2018)
data = build.data_for_seasons(seasons)

#simulate.with_data(data)
#simulate.with_bankroll(1000)
#simulate.with_methods(pickMethods)
#simulate.games_for_seasons(seasons)
