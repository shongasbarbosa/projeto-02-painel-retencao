<script setup lang="ts">
import type { EChartsOption } from 'echarts'
import { computed, onMounted, ref, watch } from 'vue'

import EChart from '@/components/EChart.vue'
import { useRetentionStore } from '@/stores/retention'

const store = useRetentionStore()
const selectedCourseIds = ref<number[]>([])

const courseOptions = computed(() => store.courses.map((c) => ({ label: c.name, value: c.id })))

async function refresh() {
  if (selectedCourseIds.value.length) {
    await store.loadComparison(selectedCourseIds.value)
  } else {
    store.comparison = []
  }
}

onMounted(async () => {
  await store.loadCourses()
  selectedCourseIds.value = store.courses.map((c) => c.id)
  await refresh()
})

watch(selectedCourseIds, refresh)

const evasionChartOption = computed<EChartsOption>(() => ({
  tooltip: { trigger: 'axis', valueFormatter: (v) => `${((v as number) * 100).toFixed(1)}%` },
  grid: { left: 8, right: 16, bottom: 8, top: 24, containLabel: true },
  xAxis: { type: 'category', data: store.comparison.map((c) => c.course_name) },
  yAxis: { type: 'value', axisLabel: { formatter: (v: number) => `${(v * 100).toFixed(0)}%` } },
  series: [
    {
      type: 'bar',
      data: store.comparison.map((c) => c.funnel.taxa_evasao),
      itemStyle: { color: '#dc2626', borderRadius: [4, 4, 0, 0] },
    },
  ],
}))

const activeVsRiskOption = computed<EChartsOption>(() => ({
  tooltip: { trigger: 'axis' },
  legend: { bottom: 0 },
  grid: { left: 8, right: 16, bottom: 40, top: 24, containLabel: true },
  xAxis: { type: 'category', data: store.comparison.map((c) => c.course_name) },
  yAxis: { type: 'value' },
  series: [
    {
      name: 'Ativos',
      type: 'bar',
      data: store.comparison.map((c) => c.funnel.ativos),
      itemStyle: { color: '#16a34a' },
    },
    {
      name: 'Em risco',
      type: 'bar',
      data: store.comparison.map((c) => c.funnel.em_risco),
      itemStyle: { color: '#d97706' },
    },
  ],
}))

const evasionSummary = computed(
  () =>
    `Taxa de evasão por turma: ${store.comparison
      .map((c) => `${c.course_name} ${(c.funnel.taxa_evasao * 100).toFixed(1)}%`)
      .join(', ')}`,
)

const activeVsRiskSummary = computed(
  () =>
    `Ativos e em risco por turma: ${store.comparison
      .map((c) => `${c.course_name}: ${c.funnel.ativos} ativos, ${c.funnel.em_risco} em risco`)
      .join('; ')}`,
)
</script>

<template>
  <q-page class="q-pa-md">
    <div class="text-h5 q-mb-md">Comparação entre turmas</div>

    <q-select
      v-model="selectedCourseIds"
      :options="courseOptions"
      option-label="label"
      option-value="value"
      emit-value
      map-options
      multiple
      dense
      outlined
      use-chips
      label="Cursos"
      class="q-mb-md"
      style="max-width: 480px"
    />

    <div class="row q-col-gutter-md">
      <div class="col-12 col-md-6">
        <q-card flat bordered>
          <q-card-section>
            <div class="text-subtitle1 q-mb-sm">Taxa de evasão</div>
            <EChart :option="evasionChartOption" :ariaLabel="evasionSummary" />
          </q-card-section>
        </q-card>
      </div>
      <div class="col-12 col-md-6">
        <q-card flat bordered>
          <q-card-section>
            <div class="text-subtitle1 q-mb-sm">Ativos vs. em risco</div>
            <EChart :option="activeVsRiskOption" :ariaLabel="activeVsRiskSummary" />
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>
