"""Kelly criterion bet sizing."""


def kelly_criterion(model_prob: float, decimal_odds: float) -> float:
    """Calculate the Kelly criterion fraction of bankroll to bet.

    Args:
        model_prob: Your estimated probability of winning.
        decimal_odds: The decimal odds offered (e.g., 2.0 for even money).

    Returns:
        Fraction of bankroll to bet (0 if no edge).
    """
    b = decimal_odds - 1  # Net odds (profit per $1 bet)
    q = 1 - model_prob
    edge = model_prob * b - q

    if edge <= 0:
        return 0.0

    return edge / b


def fractional_kelly(
    model_prob: float,
    decimal_odds: float,
    fraction: float = 0.25,
    max_bet: float = 0.05,
) -> float:
    """Kelly criterion scaled by a safety fraction and capped.

    Full Kelly is aggressive and can lead to large drawdowns.
    Quarter-Kelly (fraction=0.25) is a common conservative approach.
    """
    full_kelly = kelly_criterion(model_prob, decimal_odds)
    return min(full_kelly * fraction, max_bet)
