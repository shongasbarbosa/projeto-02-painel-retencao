<script setup lang="ts">
import * as echarts from 'echarts'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

import { useTheme } from '@/composables/useTheme'

// Tema customizado (em vez do tema 'dark' embutido do ECharts) para que o
// fundo do gráfico seja transparente e combine com o card do Quasar, e para
// que o texto tenha contraste adequado no escuro.
echarts.registerTheme('app-dark', {
  backgroundColor: 'transparent',
  textStyle: { color: '#e5e7eb' },
  title: { textStyle: { color: '#e5e7eb' } },
  legend: { textStyle: { color: '#e5e7eb' } },
  tooltip: { backgroundColor: '#1f2937', textStyle: { color: '#e5e7eb' } },
})

const props = defineProps<{
  option: echarts.EChartsOption
  height?: string
  ariaLabel: string
}>()

const { isDark } = useTheme()
const containerRef = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null
let resizeObserver: ResizeObserver | null = null

function render() {
  if (!containerRef.value) return
  chart?.dispose()
  chart = echarts.init(containerRef.value, isDark.value ? 'app-dark' : undefined)
  chart.setOption({ animation: false, ...props.option })
}

onMounted(() => {
  render()
  resizeObserver = new ResizeObserver(() => chart?.resize())
  if (containerRef.value) resizeObserver.observe(containerRef.value)
})

watch(isDark, render)
watch(
  () => props.option,
  () => chart?.setOption({ animation: false, ...props.option }),
  { deep: true },
)

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  chart?.dispose()
})
</script>

<template>
  <div>
    <div
      ref="containerRef"
      :style="{ height: height ?? '320px', width: '100%' }"
      role="img"
      :aria-label="ariaLabel"
    ></div>
    <p class="sr-only-summary">{{ ariaLabel }}</p>
  </div>
</template>

<style scoped>
.sr-only-summary {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>
