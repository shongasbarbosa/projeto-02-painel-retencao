<script setup lang="ts">
import { useTheme } from '@/composables/useTheme'
import type { ThemeChoice } from '@/composables/useTheme'

const { choice, setChoice } = useTheme()

const options: { value: ThemeChoice; label: string; icon: string }[] = [
  { value: 'system', label: 'Sistema', icon: 'brightness_auto' },
  { value: 'light', label: 'Claro', icon: 'light_mode' },
  { value: 'dark', label: 'Escuro', icon: 'dark_mode' },
]
</script>

<template>
  <div role="group" aria-label="Selecionar tema" class="theme-toggle">
    <q-btn
      v-for="option in options"
      :key="option.value"
      :icon="option.icon"
      :aria-label="option.label"
      :aria-pressed="choice === option.value"
      flat
      dense
      round
      class="theme-toggle__btn"
      :class="{ 'theme-toggle__btn--active': choice === option.value }"
      @click="setChoice(option.value)"
    >
      <q-tooltip>{{ option.label }}</q-tooltip>
    </q-btn>
  </div>
</template>

<style scoped>
.theme-toggle {
  display: flex;
  gap: 4px;
  padding: 2px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.14);
}

.theme-toggle__btn {
  min-width: 0;
  /* Ícone inativo: branco translúcido sobre o azul do cabeçalho (contraste
     AA verificado, ~5:1) — visível sem competir com o estado ativo. */
  color: rgba(255, 255, 255, 0.85);
}

.theme-toggle__btn--active {
  /* Estado ativo: fundo branco sólido com ícone na cor primária, bem
     destacado do restante do grupo (contraste AA, ~5:1). */
  background: #fff;
  color: var(--q-primary);
}
</style>
