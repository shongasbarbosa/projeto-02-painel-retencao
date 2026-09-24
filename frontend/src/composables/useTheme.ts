import { Dark } from 'quasar'
import { computed, ref } from 'vue'

export type ThemeChoice = 'system' | 'light' | 'dark'

const STORAGE_KEY = 'painel-retencao-theme'

function readStoredChoice(): ThemeChoice {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored === 'light' || stored === 'dark' || stored === 'system') {
      return stored
    }
  } catch {
    // localStorage indisponível (modo privado, storage bloqueado etc.)
  }
  return 'system'
}

function persistChoice(choice: ThemeChoice): void {
  try {
    localStorage.setItem(STORAGE_KEY, choice)
  } catch {
    // Falha silenciosa: a escolha ainda funciona na sessão atual, só não persiste.
  }
}

const choice = ref<ThemeChoice>(readStoredChoice())

function applyChoice(next: ThemeChoice): void {
  choice.value = next
  persistChoice(next)
  if (next === 'system') {
    Dark.set('auto')
  } else {
    Dark.set(next === 'dark')
  }
}

/** Deve ser chamada uma vez em main.ts, depois de `app.use(Quasar)`. */
export function initTheme(): void {
  applyChoice(choice.value)
}

export function useTheme() {
  const isDark = computed(() => Dark.isActive)

  function setChoice(next: ThemeChoice): void {
    applyChoice(next)
  }

  return {
    choice: computed(() => choice.value),
    isDark,
    setChoice,
  }
}
