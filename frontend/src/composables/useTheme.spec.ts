import { Dark } from 'quasar'
import { beforeEach, describe, expect, it, vi } from 'vitest'

describe('useTheme', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.resetModules()
  })

  it('aplica o tema "system" por padrão quando não há valor salvo', async () => {
    const { useTheme, initTheme } = await import('./useTheme')
    initTheme()
    const { choice } = useTheme()
    expect(choice.value).toBe('system')
  })

  it('troca de tema e chama Dark.set corretamente', async () => {
    const spy = vi.spyOn(Dark, 'set')
    const { useTheme, initTheme } = await import('./useTheme')
    initTheme()
    const { setChoice } = useTheme()

    setChoice('dark')
    expect(spy).toHaveBeenCalledWith(true)

    setChoice('light')
    expect(spy).toHaveBeenCalledWith(false)

    setChoice('system')
    expect(spy).toHaveBeenCalledWith('auto')
  })

  it('persiste a escolha no localStorage', async () => {
    const { useTheme, initTheme } = await import('./useTheme')
    initTheme()
    const { setChoice } = useTheme()

    setChoice('dark')
    expect(localStorage.getItem('painel-retencao-theme')).toBe('dark')
  })

  it('recupera a escolha salva do localStorage ao iniciar', async () => {
    localStorage.setItem('painel-retencao-theme', 'light')
    const { useTheme, initTheme } = await import('./useTheme')
    initTheme()
    const { choice } = useTheme()
    expect(choice.value).toBe('light')
  })

  it('não quebra quando localStorage lança erro (fallback para "system")', async () => {
    const getItemSpy = vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new Error('storage bloqueado')
    })
    const setItemSpy = vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('storage bloqueado')
    })

    const { useTheme, initTheme } = await import('./useTheme')
    expect(() => initTheme()).not.toThrow()
    const { choice, setChoice } = useTheme()
    expect(choice.value).toBe('system')
    expect(() => setChoice('dark')).not.toThrow()

    getItemSpy.mockRestore()
    setItemSpy.mockRestore()
  })
})
