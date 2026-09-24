import { describe, expect, it } from 'vitest'

import { calculateRiskScore, classifyRisk } from './riskScore'

describe('calculateRiskScore', () => {
  it('retorna 0 para aluno totalmente engajado', () => {
    expect(calculateRiskScore(0, 1)).toBe(0)
  })

  it('retorna 1 para aluno totalmente desengajado', () => {
    expect(calculateRiskScore(60, 0)).toBe(1)
  })

  it('satura o componente de inatividade em 30 dias', () => {
    expect(calculateRiskScore(30, 1)).toBe(calculateRiskScore(90, 1))
  })

  it('segue a fórmula 0.6 * inatividade + 0.4 * (1 - entregas)', () => {
    const score = calculateRiskScore(15, 0.5)
    expect(score).toBeCloseTo(0.6 * 0.5 + 0.4 * 0.5, 4)
  })
})

describe('classifyRisk', () => {
  it('classifica corretamente as faixas', () => {
    expect(classifyRisk(0)).toBe('baixo')
    expect(classifyRisk(0.39)).toBe('baixo')
    expect(classifyRisk(0.4)).toBe('medio')
    expect(classifyRisk(0.7)).toBe('medio')
    expect(classifyRisk(0.71)).toBe('alto')
    expect(classifyRisk(1)).toBe('alto')
  })
})
