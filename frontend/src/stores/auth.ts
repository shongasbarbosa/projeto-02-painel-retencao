import { defineStore } from 'pinia'
import { ref } from 'vue'

import { getRetentionService, isDemoMode } from '@/services'

export const useAuthStore = defineStore('auth', () => {
  const service = getRetentionService()
  const isAuthenticated = ref(service.isAuthenticated())
  const error = ref<string | null>(null)
  const loading = ref(false)

  async function login(email: string, password: string): Promise<boolean> {
    loading.value = true
    error.value = null
    try {
      await service.login(email, password)
      isAuthenticated.value = true
      return true
    } catch {
      error.value = 'E-mail ou senha inválidos.'
      isAuthenticated.value = false
      return false
    } finally {
      loading.value = false
    }
  }

  function logout(): void {
    service.logout()
    isAuthenticated.value = false
  }

  return { isAuthenticated, error, loading, login, logout, isDemoMode }
})
