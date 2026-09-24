"""Testes da regra pura de score de risco."""

import pytest

from app.services.risk_score import RiskLevel, calculate_risk_score, classify_risk


def test_score_zero_when_fully_engaged():
    score = calculate_risk_score(days_inactive=0, submission_rate=1.0)
    assert score == 0.0


def test_score_max_when_fully_disengaged():
    score = calculate_risk_score(days_inactive=60, submission_rate=0.0)
    assert score == 1.0


def test_score_caps_inactivity_component_at_30_days():
    score_30 = calculate_risk_score(days_inactive=30, submission_rate=1.0)
    score_90 = calculate_risk_score(days_inactive=90, submission_rate=1.0)
    assert score_30 == score_90 == 0.6

    score_30_no_sub = calculate_risk_score(days_inactive=30, submission_rate=0.0)
    score_90_no_sub = calculate_risk_score(days_inactive=90, submission_rate=0.0)
    assert score_30_no_sub == score_90_no_sub == 1.0


def test_score_matches_formula():
    score = calculate_risk_score(days_inactive=15, submission_rate=0.5)
    expected = round(0.6 * (15 / 30) + 0.4 * (1 - 0.5), 4)
    assert score == expected


@pytest.mark.parametrize(
    ("days_inactive", "submission_rate"),
    [(-1, 0.5), (5, -0.1), (5, 1.1)],
)
def test_invalid_inputs_raise(days_inactive, submission_rate):
    with pytest.raises(ValueError):
        calculate_risk_score(days_inactive, submission_rate)


@pytest.mark.parametrize(
    ("score", "level"),
    [
        (0.0, RiskLevel.BAIXO),
        (0.39, RiskLevel.BAIXO),
        (0.4, RiskLevel.MEDIO),
        (0.7, RiskLevel.MEDIO),
        (0.71, RiskLevel.ALTO),
        (1.0, RiskLevel.ALTO),
    ],
)
def test_classify_risk_boundaries(score, level):
    assert classify_risk(score) == level
