import { defineStore } from 'pinia'
import { ref } from 'vue'

import { getRetentionService } from '@/services'
import type {
  ComparisonItem,
  ContactLogInput,
  Course,
  FunnelReport,
  RiskLevel,
  RiskScoreItem,
} from '@/services'

export const useRetentionStore = defineStore('retention', () => {
  const service = getRetentionService()

  const courses = ref<Course[]>([])
  const funnel = ref<FunnelReport | null>(null)
  const riskItems = ref<RiskScoreItem[]>([])
  const comparison = ref<ComparisonItem[]>([])
  const loading = ref(false)

  async function loadCourses(): Promise<void> {
    courses.value = await service.listCourses()
  }

  async function loadFunnel(courseId?: number): Promise<void> {
    funnel.value = await service.getFunnel(courseId)
  }

  async function loadRiskItems(courseId?: number, level?: RiskLevel): Promise<void> {
    loading.value = true
    try {
      riskItems.value = await service.getRiskScore(courseId, level)
    } finally {
      loading.value = false
    }
  }

  async function loadComparison(courseIds: number[]): Promise<void> {
    comparison.value = await service.getComparison(courseIds)
  }

  async function registerContact(studentId: number, input: ContactLogInput): Promise<void> {
    await service.createContactLog(studentId, input)
  }

  async function loadContactHistory(studentId: number) {
    return service.listContactLogs(studentId)
  }

  async function exportCsv(courseId?: number): Promise<string> {
    return service.getRiskScoreCsv(courseId)
  }

  return {
    courses,
    funnel,
    riskItems,
    comparison,
    loading,
    loadCourses,
    loadFunnel,
    loadRiskItems,
    loadComparison,
    registerContact,
    loadContactHistory,
    exportCsv,
  }
})
