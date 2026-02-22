"""Betting simulation and backtesting engine."""

import logging

import pandas as pd

from charliehustle.betting.kelly import fractional_kelly
from charliehustle.betting.odds import american_to_decimal, implied_prob_to_american
from charliehustle.config import DEFAULT_CONFIG, Config

logger = logging.getLogger(__name__)


def backtest(
    games: pd.DataFrame,
    config: Config = DEFAULT_CONFIG,
) -> pd.DataFrame:
    """Run a betting simulation over predicted games.

    Expects columns: home_win, model_home_prob, home_team, away_team.
    Optionally: home_line, away_line (American odds) for real odds.

    Returns a DataFrame with one row per bet placed, tracking bankroll.
    """
    bankroll = config.initial_bankroll
    has_odds = "home_line" in games.columns and "away_line" in games.columns

    bets: list[dict] = []

    for _, game in games.iterrows():
        model_home_prob = game["model_home_prob"]
        model_away_prob = 1 - model_home_prob

        # Pick the side with higher model probability
        if model_home_prob >= 0.5:
            pick = game["home_team"]
            pick_prob = model_home_prob
            is_home_pick = True
        else:
            pick = game["away_team"]
            pick_prob = model_away_prob
            is_home_pick = False

        # Determine odds
        if has_odds:
            pick_line = (
                game["home_line"] if is_home_pick else game["away_line"]
            )
            decimal_odds = american_to_decimal(float(pick_line))
        else:
            # Synthesize odds from model probability with ~5% vig
            fair_line = implied_prob_to_american(1 - pick_prob)
            decimal_odds = american_to_decimal(fair_line) * 0.95

        # Kelly criterion sizing
        bet_fraction = fractional_kelly(
            pick_prob,
            decimal_odds,
            fraction=config.kelly_fraction,
            max_bet=config.max_bet_fraction,
        )

        # Check minimum edge
        implied_prob = 1 / decimal_odds
        edge = pick_prob - implied_prob
        if edge < config.min_edge:
            continue

        bet_amount = round(bankroll * bet_fraction, 2)
        if bet_amount < 1.0:
            continue

        # Resolve bet
        actual_winner = (
            game["home_team"] if game["home_win"] else game["away_team"]
        )
        won = pick == actual_winner

        if won:
            payout = round(bet_amount * (decimal_odds - 1), 2)
        else:
            payout = -bet_amount

        bankroll = round(bankroll + payout, 2)

        bets.append(
            {
                "date": game["date"],
                "home_team": game["home_team"],
                "away_team": game["away_team"],
                "pick": pick,
                "pick_prob": round(pick_prob, 4),
                "edge": round(edge, 4),
                "decimal_odds": round(decimal_odds, 4),
                "bet_fraction": round(bet_fraction, 4),
                "bet_amount": bet_amount,
                "won": won,
                "payout": payout,
                "bankroll": bankroll,
            }
        )

    results = pd.DataFrame(bets)

    if len(results) > 0:
        _print_summary(results, config.initial_bankroll)
    else:
        print("No bets placed (no edges found).")

    return results


def _print_summary(results: pd.DataFrame, initial_bankroll: float) -> None:
    """Print a summary of the backtest results."""
    total_bets = len(results)
    wins = int(results["won"].sum())
    losses = total_bets - wins
    final_bankroll = results["bankroll"].iloc[-1]
    roi = (final_bankroll - initial_bankroll) / initial_bankroll

    peak = results["bankroll"].max()
    trough = results["bankroll"].min()
    max_drawdown = initial_bankroll - trough

    print(f"\n{'=' * 50}")
    print("  Backtest Results")
    print(f"{'=' * 50}")
    print(f"  Record:          {wins}W - {losses}L ({wins / total_bets:.1%})")
    print(f"  Total Bets:      {total_bets}")
    print(f"  Starting Bank:   ${initial_bankroll:,.2f}")
    print(f"  Ending Bank:     ${final_bankroll:,.2f}")
    print(f"  ROI:             {roi:+.1%}")
    print(f"  Peak:            ${peak:,.2f}")
    print(f"  Avg Edge:        {results['edge'].mean():.1%}")
    print(
        f"  Avg Bet Size:    {results['bet_fraction'].mean():.2%} of bankroll"
    )
    print(f"  Max Drawdown:    ${max_drawdown:,.2f}")
    print(f"{'=' * 50}\n")
