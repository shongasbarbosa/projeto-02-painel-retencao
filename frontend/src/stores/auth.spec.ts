import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const mockService = {
  login: vi.fn(),
  logout: vi.fn(),
  isAuthenticated: vi.fn(() => false),
}

vi.mock('@/services', () => ({
  getRetentionService: () => mockService,
  isDemoMode: true,
}))

describe('useAuthStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    mockService.login.mockReset()
    mockService.logout.mockReset()
    mockService.isAuthenticated.mockReset().mockReturnValue(false)
  })

  it('starts unauthenticated when the service has no session', async () => {
    const { useAuthStore } = await import('./auth')
    const store = useAuthStore()
    expect(store.isAuthenticated).toBe(false)
  })

  it('sets isAuthenticated to true on successful login', async () => {
    mockService.login.mockResolvedValue(undefined)
    const { useAuthStore } = await import('./auth')
    const store = useAuthStore()

    const ok = await store.login('demo@painelretencao.com', 'demo123456')

    expect(ok).toBe(true)
    expect(store.isAuthenticated).toBe(true)
    expect(store.error).toBeNull()
    expect(mockService.login).toHaveBeenCalledWith('demo@painelretencao.com', 'demo123456')
  })

  it('keeps isAuthenticated false and sets an error on failed login', async () => {
    mockService.login.mockRejectedValue(new Error('unauthorized'))
    const { useAuthStore } = await import('./auth')
    const store = useAuthStore()

    const ok = await store.login('demo@painelretencao.com', 'senha-errada')

    expect(ok).toBe(false)
    expect(store.isAuthenticated).toBe(false)
    expect(store.error).not.toBeNull()
  })

  it('clears isAuthenticated and calls the service on logout', async () => {
    mockService.login.mockResolvedValue(undefined)
    const { useAuthStore } = await import('./auth')
    const store = useAuthStore()

    await store.login('demo@painelretencao.com', 'demo123456')
    expect(store.isAuthenticated).toBe(true)

    store.logout()

    expect(store.isAuthenticated).toBe(false)
    expect(mockService.logout).toHaveBeenCalledOnce()
  })
})
