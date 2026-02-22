"""Tests for odds conversion and Kelly criterion."""

import pytest

from charliehustle.betting.kelly import fractional_kelly, kelly_criterion
from charliehustle.betting.odds import (
    american_to_decimal,
    american_to_implied_prob,
    decimal_to_american,
    implied_prob_to_american,
)


class TestAmericanToDecimal:
    def test_positive_odds(self):
        assert american_to_decimal(150) == 2.5

    def test_negative_odds(self):
        assert abs(american_to_decimal(-150) - 1.6667) < 0.001

    def test_even_money(self):
        assert american_to_decimal(100) == 2.0


class TestDecimalToAmerican:
    def test_underdog(self):
        assert decimal_to_american(2.5) == 150.0

    def test_favorite(self):
        assert abs(decimal_to_american(1.5) - (-200)) < 0.01


class TestImpliedProbability:
    def test_favorite(self):
        assert abs(american_to_implied_prob(-150) - 0.6) < 0.001

    def test_underdog(self):
        assert abs(american_to_implied_prob(150) - 0.4) < 0.001

    def test_round_trip(self):
        for prob in [0.3, 0.4, 0.5, 0.6, 0.7]:
            american = implied_prob_to_american(prob)
            back = american_to_implied_prob(american)
            assert abs(back - prob) < 0.001, f"Round trip failed for {prob}"


class TestOddsRoundTrip:
    @pytest.mark.parametrize("odds", [-200, -150, -110, 100, 110, 150, 200])
    def test_american_decimal_round_trip(self, odds):
        decimal = american_to_decimal(odds)
        back = decimal_to_american(decimal)
        assert abs(back - odds) < 0.01


class TestKellyCriterion:
    def test_no_edge_returns_zero(self):
        assert kelly_criterion(0.5, 2.0) == 0.0

    def test_positive_edge(self):
        kelly = kelly_criterion(0.55, 2.0)
        assert kelly == pytest.approx(0.1, abs=0.001)

    def test_negative_edge_returns_zero(self):
        assert kelly_criterion(0.45, 2.0) == 0.0

    def test_large_edge(self):
        kelly = kelly_criterion(0.8, 2.0)
        assert kelly > 0.5


class TestFractionalKelly:
    def test_scales_by_fraction(self):
        full = kelly_criterion(0.6, 2.0)
        quarter = fractional_kelly(0.6, 2.0, fraction=0.25)
        assert abs(quarter - full * 0.25) < 0.001

    def test_respects_cap(self):
        capped = fractional_kelly(0.9, 2.0, fraction=1.0, max_bet=0.05)
        assert capped == 0.05

    def test_no_edge_returns_zero(self):
        assert fractional_kelly(0.5, 2.0) == 0.0
