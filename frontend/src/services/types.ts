export type EnrollmentStatus = 'ativo' | 'desistente' | 'concluido'
export type RiskLevel = 'baixo' | 'medio' | 'alto'
export type ContactOutcome = 'sem_resposta' | 'retornou' | 'desistiu'

export interface Course {
  id: number
  name: string
  category: string
}

export interface FunnelReport {
  matriculados: number
  ativos: number
  em_risco: number
  desistentes: number
  concluintes: number
  taxa_evasao: number
}

export interface RiskScoreItem {
  enrollment_id: number
  student_id: number
  student_name: string
  course_id: number
  course_name: string
  days_inactive: number
  submission_rate: number
  score: number
  level: RiskLevel
}

export interface ComparisonItem {
  course_id: number
  course_name: string
  funnel: FunnelReport
}

export interface ContactLog {
  id: number
  student_id: number
  course_id: number
  contacted_at: string
  outcome: ContactOutcome
  notes: string | null
}

export interface ContactLogInput {
  course_id: number
  outcome: ContactOutcome
  notes?: string
}

export interface RetentionService {
  login(email: string, password: string): Promise<void>
  logout(): void
  isAuthenticated(): boolean
  listCourses(): Promise<Course[]>
  getFunnel(courseId?: number): Promise<FunnelReport>
  getRiskScore(courseId?: number, level?: RiskLevel): Promise<RiskScoreItem[]>
  getComparison(courseIds: number[]): Promise<ComparisonItem[]>
  createContactLog(studentId: number, input: ContactLogInput): Promise<ContactLog>
  listContactLogs(studentId: number): Promise<ContactLog[]>
  getRiskScoreCsv(courseId?: number): Promise<string>
}
