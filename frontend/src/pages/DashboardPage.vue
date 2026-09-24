<script setup lang="ts">
import type { EChartsOption } from 'echarts'
import { computed, onMounted, ref, watch } from 'vue'

import EChart from '@/components/EChart.vue'
import { useTheme } from '@/composables/useTheme'
import { useRetentionStore } from '@/stores/retention'

const store = useRetentionStore()
const { isDark } = useTheme()
const selectedCourseId = ref<number | null>(null)

const courseOptions = computed(() => [
  { label: 'Todos os cursos', value: null },
  ...store.courses.map((c) => ({ label: c.name, value: c.id })),
])

async function refresh() {
  await store.loadFunnel(selectedCourseId.value ?? undefined)
  await store.loadRiskItems(selectedCourseId.value ?? undefined)
}

onMounted(async () => {
  await store.loadCourses()
  await refresh()
})

watch(selectedCourseId, refresh)

const kpis = computed(() => {
  const f = store.funnel
  if (!f) return []
  return [
    { label: 'Matriculados', value: f.matriculados, color: 'primary' },
    { label: 'Ativos', value: f.ativos, color: 'positive' },
    { label: 'Em risco', value: f.em_risco, color: 'warning' },
    { label: 'Desistentes', value: f.desistentes, color: 'negative' },
    { label: 'Concluintes', value: f.concluintes, color: 'info' },
    { label: 'Taxa de evasão', value: `${(f.taxa_evasao * 100).toFixed(1)}%`, color: 'negative' },
  ]
})

const funnelChartOption = computed<EChartsOption>(() => {
  const f = store.funnel
  const categories = ['Matriculados', 'Ativos', 'Em risco', 'Desistentes', 'Concluintes']
  const values = f ? [f.matriculados, f.ativos, f.em_risco, f.desistentes, f.concluintes] : []
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: 8, right: 16, bottom: 8, top: 24, containLabel: true },
    xAxis: { type: 'category', data: categories },
    yAxis: { type: 'value' },
    series: [{ type: 'bar', data: values, itemStyle: { borderRadius: [4, 4, 0, 0] } }],
  }
})

const riskDistributionOption = computed<EChartsOption>(() => {
  const counts = { baixo: 0, medio: 0, alto: 0 }
  for (const item of store.riskItems) counts[item.level]++
  return {
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [
      {
        type: 'pie',
        radius: ['45%', '70%'],
        label: {
          color: isDark.value ? '#e5e7eb' : '#1f2937',
          textBorderWidth: 0,
        },
        labelLine: {
          lineStyle: { color: isDark.value ? '#6b7280' : '#9ca3af' },
        },
        data: [
          { name: 'Baixo risco', value: counts.baixo, itemStyle: { color: '#16a34a' } },
          { name: 'Médio risco', value: counts.medio, itemStyle: { color: '#d97706' } },
          { name: 'Alto risco', value: counts.alto, itemStyle: { color: '#dc2626' } },
        ],
      },
    ],
  }
})

const funnelSummary = computed(() => {
  const f = store.funnel
  if (!f) return 'Sem dados.'
  return `Funil: ${f.matriculados} matriculados, ${f.ativos} ativos, ${f.em_risco} em risco, ${f.desistentes} desistentes, ${f.concluintes} concluintes.`
})

const riskSummary = computed(() => {
  const counts = { baixo: 0, medio: 0, alto: 0 }
  for (const item of store.riskItems) counts[item.level]++
  return `Distribuição de risco: ${counts.baixo} baixo, ${counts.medio} médio, ${counts.alto} alto.`
})
</script>

<template>
  <q-page class="q-pa-md dashboard-page">
    <div class="row items-center q-mb-md q-gutter-sm">
      <div class="text-h5">Dashboard</div>
      <q-space />
      <q-select
        v-model="selectedCourseId"
        :options="courseOptions"
        option-label="label"
        option-value="value"
        emit-value
        map-options
        dense
        outlined
        label="Curso"
        style="min-width: 220px"
      />
    </div>

    <div class="row q-col-gutter-md q-mb-md">
      <div v-for="kpi in kpis" :key="kpi.label" class="col-6 col-sm-4 col-md-2">
        <q-card flat bordered class="kpi-card">
          <q-card-section>
            <div class="text-caption text-grey-7">{{ kpi.label }}</div>
            <div class="text-h5" :class="`text-${kpi.color}`">{{ kpi.value }}</div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <div class="row q-col-gutter-md">
      <div class="col-12 col-md-7">
        <q-card flat bordered>
          <q-card-section>
            <div class="text-subtitle1 q-mb-sm">Funil de retenção</div>
            <EChart :option="funnelChartOption" :ariaLabel="funnelSummary" />
          </q-card-section>
        </q-card>
      </div>
      <div class="col-12 col-md-5">
        <q-card flat bordered>
          <q-card-section>
            <div class="text-subtitle1 q-mb-sm">Distribuição por faixa de risco</div>
            <EChart :option="riskDistributionOption" :ariaLabel="riskSummary" />
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<style scoped>
.kpi-card {
  height: 100%;
}
</style>
