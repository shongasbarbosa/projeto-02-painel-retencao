"""Regra de cálculo do score de risco de evasão.

Esta é uma função pura para permitir testes isolados e reaproveitamento
futuro no plugin Moodle (projeto 5 do portfólio).

score = 0.6 * min(dias_inativo / 30, 1) + 0.4 * (1 - % atividades entregues)
"""

from enum import StrEnum


class RiskLevel(StrEnum):
    BAIXO = "baixo"
    MEDIO = "medio"
    ALTO = "alto"


def calculate_risk_score(days_inactive: int, submission_rate: float) -> float:
    """Calcula o score de risco (0 a 1) a partir dos dias de inatividade
    e da taxa de entregas (0 a 1)."""
    if days_inactive < 0:
        raise ValueError("days_inactive não pode ser negativo")
    if not 0 <= submission_rate <= 1:
        raise ValueError("submission_rate deve estar entre 0 e 1")

    inactivity_component = min(days_inactive / 30, 1)
    submission_component = 1 - submission_rate
    return round(0.6 * inactivity_component + 0.4 * submission_component, 4)


def classify_risk(score: float) -> RiskLevel:
    """Classifica o score em faixas: baixo (<0.4), médio (0.4-0.7), alto (>0.7)."""
    if score < 0.4:
        return RiskLevel.BAIXO
    if score <= 0.7:
        return RiskLevel.MEDIO
    return RiskLevel.ALTO
