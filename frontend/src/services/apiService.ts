import axios, { type AxiosInstance } from 'axios'

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

const TOKEN_KEY = 'painel-retencao-token'
const baseURL = import.meta.env.VITE_API_URL ?? ''

function createHttpClient(): AxiosInstance {
  const client = axios.create({ baseURL })
  client.interceptors.request.use((config) => {
    const token = localStorage.getItem(TOKEN_KEY)
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  })
  return client
}

export function createApiService(): RetentionService {
  const http = createHttpClient()

  return {
    async login(email, password) {
      const { data } = await http.post<{ access_token: string }>('/api/auth/login', {
        email,
        password,
      })
      localStorage.setItem(TOKEN_KEY, data.access_token)
    },

    logout() {
      localStorage.removeItem(TOKEN_KEY)
    },

    isAuthenticated() {
      return Boolean(localStorage.getItem(TOKEN_KEY))
    },

    async listCourses() {
      const { data } = await http.get<Course[]>('/api/courses')
      return data
    },

    async getFunnel(courseId) {
      const { data } = await http.get<FunnelReport>('/api/reports/funnel', {
        params: { course_id: courseId },
      })
      return data
    },

    async getRiskScore(courseId?: number, level?: RiskLevel) {
      const { data } = await http.get<RiskScoreItem[]>('/api/reports/risk-score', {
        params: { course_id: courseId, level },
      })
      return data
    },

    async getComparison(courseIds) {
      const { data } = await http.get<ComparisonItem[]>('/api/reports/comparison', {
        params: { course_ids: courseIds.join(',') },
      })
      return data
    },

    async createContactLog(studentId: number, input: ContactLogInput) {
      const { data } = await http.post<ContactLog>(`/api/students/${studentId}/contact-logs`, input)
      return data
    },

    async listContactLogs(studentId: number) {
      const { data } = await http.get<ContactLog[]>(`/api/students/${studentId}/contact-logs`)
      return data
    },

    async getRiskScoreCsv(courseId?: number) {
      const { data } = await http.get<string>('/api/reports/risk-score/export', {
        params: { course_id: courseId },
        responseType: 'text',
      })
      return data
    },
  }
}
