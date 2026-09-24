import type { RiskLevel } from './types'

/**
 * Mesma regra usada no backend (app/services/risk_score.py):
 * score = 0.6 * min(dias_inativo / 30, 1) + 0.4 * (1 - % atividades entregues)
 */
export function calculateRiskScore(daysInactive: number, submissionRate: number): number {
  const inactivityComponent = Math.min(daysInactive / 30, 1)
  const submissionComponent = 1 - submissionRate
  return Math.round((0.6 * inactivityComponent + 0.4 * submissionComponent) * 10000) / 10000
}

export function classifyRisk(score: number): RiskLevel {
  if (score < 0.4) return 'baixo'
  if (score <= 0.7) return 'medio'
  return 'alto'
}
