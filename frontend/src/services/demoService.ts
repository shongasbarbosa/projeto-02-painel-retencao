import seedData from '@/demo-data/seed.json'

import { calculateRiskScore, classifyRisk } from './riskScore'
import type {
  ComparisonItem,
  ContactLog,
  ContactLogInput,
  Course,
  FunnelReport,
  RetentionService,
  RiskLevel,
  RiskScoreItem,
} from './types'

interface SeedEnrollment {
  student: { id: number; name: string; email: string }
  enrollment: {
    id: number
    course_id: number
    status: 'ativo' | 'desistente' | 'concluido'
    enrolled_at: string
    last_access_at: string | null
    completed_at: string | null
  }
  submission_rate: number
}

interface SeedData {
  generated_at: string
  courses: Course[]
  activities: { id: number; course_id: number; title: string; weight: number }[]
  enrollments: SeedEnrollment[]
}

const data = seedData as SeedData

let nextContactLogId = 1000000
const contactLogs: ContactLog[] = []

function daysBetween(from: string, to: Date): number {
  const fromDate = new Date(from)
  const diffMs = to.getTime() - fromDate.getTime()
  return Math.max(Math.floor(diffMs / (1000 * 60 * 60 * 24)), 0)
}

function buildRiskItems(courseId?: number, level?: RiskLevel): RiskScoreItem[] {
  const now = new Date()
  const items: RiskScoreItem[] = data.enrollments
    .filter((e) => e.enrollment.status === 'ativo')
    .filter((e) => (courseId ? e.enrollment.course_id === courseId : true))
    .map((e) => {
      const lastMoment = e.enrollment.last_access_at ?? e.enrollment.enrolled_at
      const days = daysBetween(lastMoment, now)
      const score = calculateRiskScore(days, e.submission_rate)
      const course = data.courses.find((c) => c.id === e.enrollment.course_id)
      return {
        enrollment_id: e.enrollment.id,
        student_id: e.student.id,
        student_name: e.student.name,
        course_id: e.enrollment.course_id,
        course_name: course?.name ?? '—',
        days_inactive: days,
        submission_rate: e.submission_rate,
        score,
        level: classifyRisk(score),
      }
    })
    .filter((item) => (level ? item.level === level : true))

  return items.sort((a, b) => b.score - a.score)
}

function buildFunnel(courseId?: number): FunnelReport {
  const enrollments = data.enrollments.filter((e) =>
    courseId ? e.enrollment.course_id === courseId : true,
  )
  const matriculados = enrollments.length
  const ativos = enrollments.filter((e) => e.enrollment.status === 'ativo').length
  const desistentes = enrollments.filter((e) => e.enrollment.status === 'desistente').length
  const concluintes = enrollments.filter((e) => e.enrollment.status === 'concluido').length
  const emRisco = buildRiskItems(courseId).filter((item) => item.level !== 'baixo').length

  return {
    matriculados,
    ativos,
    em_risco: emRisco,
    desistentes,
    concluintes,
    taxa_evasao: matriculados ? Math.round((desistentes / matriculados) * 10000) / 10000 : 0,
  }
}

export function createDemoService(): RetentionService {
  return {
    async login() {
      localStorage.setItem('painel-retencao-demo-auth', '1')
    },

    logout() {
      localStorage.removeItem('painel-retencao-demo-auth')
      contactLogs.length = 0
    },

    isAuthenticated() {
      return Boolean(localStorage.getItem('painel-retencao-demo-auth'))
    },

    async listCourses(): Promise<Course[]> {
      return data.courses
    },

    async getFunnel(courseId?: number) {
      return buildFunnel(courseId)
    },

    async getRiskScore(courseId?: number, level?: RiskLevel) {
      return buildRiskItems(courseId, level)
    },

    async getComparison(courseIds: number[]): Promise<ComparisonItem[]> {
      return courseIds
        .map((id) => data.courses.find((c) => c.id === id))
        .filter((c): c is Course => Boolean(c))
        .map((course) => ({
          course_id: course.id,
          course_name: course.name,
          funnel: buildFunnel(course.id),
        }))
    },

    async createContactLog(studentId: number, input: ContactLogInput): Promise<ContactLog> {
      const log: ContactLog = {
        id: nextContactLogId++,
        student_id: studentId,
        course_id: input.course_id,
        contacted_at: new Date().toISOString(),
        outcome: input.outcome,
        notes: input.notes ?? null,
      }
      contactLogs.unshift(log)
      return log
    },

    async listContactLogs(studentId: number): Promise<ContactLog[]> {
      return contactLogs.filter((log) => log.student_id === studentId)
    },

    async getRiskScoreCsv(courseId?: number) {
      const items = buildRiskItems(courseId)
      const header = [
        'enrollment_id',
        'student_id',
        'student_name',
        'course_id',
        'course_name',
        'days_inactive',
        'submission_rate',
        'score',
        'level',
      ]
      const rows = items.map((item) =>
        [
          item.enrollment_id,
          item.student_id,
          item.student_name,
          item.course_id,
          item.course_name,
          item.days_inactive,
          item.submission_rate,
          item.score,
          item.level,
        ].join(','),
      )
      return [header.join(','), ...rows].join('\n')
    },
  }
}
