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
      :color="choice === option.value ? 'primary' : 'grey-7'"
      :flat="choice !== option.value"
      :unelevated="choice === option.value"
      dense
      round
      class="theme-toggle__btn"
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
  background: rgba(128, 128, 128, 0.12);
}

.theme-toggle__btn {
  min-width: 0;
}
</style>
