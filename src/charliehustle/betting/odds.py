"""Odds conversion utilities."""


def american_to_decimal(american: float) -> float:
    """Convert American odds to decimal odds.

    Examples:
        +150 -> 2.50  (bet $100, get $250 back)
        -150 -> 1.667 (bet $150, get $250 back)
    """
    if american > 0:
        return american / 100 + 1
    return 100 / abs(american) + 1


def decimal_to_american(decimal: float) -> float:
    """Convert decimal odds to American odds."""
    if decimal >= 2.0:
        return (decimal - 1) * 100
    return -100 / (decimal - 1)


def american_to_implied_prob(american: float) -> float:
    """Convert American odds to implied probability (no-vig).

    Examples:
        -150 -> 0.600
        +150 -> 0.400
    """
    if american < 0:
        return abs(american) / (abs(american) + 100)
    return 100 / (american + 100)


def implied_prob_to_american(prob: float) -> float:
    """Convert implied probability to American odds."""
    if prob >= 0.5:
        return -(prob / (1 - prob)) * 100
    return ((1 - prob) / prob) * 100
