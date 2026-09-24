import { createApiService } from './apiService'
import { createDemoService } from './demoService'
import type { RetentionService } from './types'

export const isDemoMode = import.meta.env.VITE_DEMO_MODE === 'true'

let instance: RetentionService | null = null

export function getRetentionService(): RetentionService {
  if (!instance) {
    instance = isDemoMode ? createDemoService() : createApiService()
  }
  return instance
}

export * from './types'
