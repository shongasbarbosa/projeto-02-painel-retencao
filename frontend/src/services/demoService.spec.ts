import { beforeEach, describe, expect, it, vi } from 'vitest'

const now = new Date()
const daysAgo = (n: number) => new Date(now.getTime() - n * 24 * 60 * 60 * 1000).toISOString()

vi.mock('@/demo-data/seed.json', () => ({
  default: {
    generated_at: now.toISOString(),
    courses: [
      { id: 1, name: 'Curso A', category: 'Tecnologia' },
      { id: 2, name: 'Curso B', category: 'Negócios' },
    ],
    activities: [],
    enrollments: [
      {
        student: { id: 1, name: 'Aluno Engajado', email: 'a@teste.com' },
        enrollment: {
          id: 1,
          course_id: 1,
          status: 'ativo',
          enrolled_at: daysAgo(20),
          last_access_at: daysAgo(0),
          completed_at: null,
        },
        submission_rate: 1,
      },
      {
        student: { id: 2, name: 'Aluno Desengajado', email: 'b@teste.com' },
        enrollment: {
          id: 2,
          course_id: 1,
          status: 'ativo',
          enrolled_at: daysAgo(60),
          last_access_at: daysAgo(45),
          completed_at: null,
        },
        submission_rate: 0,
      },
      {
        student: { id: 3, name: 'Aluno Desistente', email: 'c@teste.com' },
        enrollment: {
          id: 3,
          course_id: 2,
          status: 'desistente',
          enrolled_at: daysAgo(90),
          last_access_at: daysAgo(70),
          completed_at: null,
        },
        submission_rate: 0.1,
      },
    ],
  },
}))

describe('demoService', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.resetModules()
  })

  it('lista os cursos do seed', async () => {
    const { createDemoService } = await import('./demoService')
    const service = createDemoService()
    const courses = await service.listCourses()
    expect(courses).toHaveLength(2)
  })

  it('ordena a lista de risco por score decrescente', async () => {
    const { createDemoService } = await import('./demoService')
    const service = createDemoService()
    const items = await service.getRiskScore(1)
    expect(items).toHaveLength(2)
    expect(items[0].student_name).toBe('Aluno Desengajado')
    expect(items[0].score).toBeGreaterThan(items[1].score)
  })

  it('calcula o funil considerando status das matrículas', async () => {
    const { createDemoService } = await import('./demoService')
    const service = createDemoService()
    const funnel = await service.getFunnel()
    expect(funnel.matriculados).toBe(3)
    expect(funnel.desistentes).toBe(1)
    expect(funnel.taxa_evasao).toBeCloseTo(1 / 3, 4)
  })

  it('registra e lista contatos em memória', async () => {
    const { createDemoService } = await import('./demoService')
    const service = createDemoService()
    await service.createContactLog(2, { course_id: 1, outcome: 'sem_resposta' })
    const logs = await service.listContactLogs(2)
    expect(logs).toHaveLength(1)
    expect(logs[0].outcome).toBe('sem_resposta')
  })

  it('mantém login demo em memória via localStorage', async () => {
    const { createDemoService } = await import('./demoService')
    const service = createDemoService()
    expect(service.isAuthenticated()).toBe(false)
    await service.login('demo@painelretencao.com', 'demo123456')
    expect(service.isAuthenticated()).toBe(true)
    service.logout()
    expect(service.isAuthenticated()).toBe(false)
  })
})
