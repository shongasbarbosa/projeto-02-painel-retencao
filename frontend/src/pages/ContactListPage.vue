<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

import type { ContactLog, ContactOutcome, RiskLevel, RiskScoreItem } from '@/services'
import { useRetentionStore } from '@/stores/retention'

const store = useRetentionStore()

const selectedCourseId = ref<number | null>(null)
const selectedLevel = ref<RiskLevel | null>(null)
const search = ref('')

const courseOptions = computed(() => [
  { label: 'Todos os cursos', value: null },
  ...store.courses.map((c) => ({ label: c.name, value: c.id })),
])

const levelOptions = [
  { label: 'Todas as faixas', value: null },
  { label: 'Baixo', value: 'baixo' as RiskLevel },
  { label: 'Médio', value: 'medio' as RiskLevel },
  { label: 'Alto', value: 'alto' as RiskLevel },
]

async function refresh() {
  await store.loadRiskItems(selectedCourseId.value ?? undefined, selectedLevel.value ?? undefined)
}

onMounted(async () => {
  await store.loadCourses()
  await refresh()
})

watch([selectedCourseId, selectedLevel], refresh)

const filteredItems = computed(() => {
  const term = search.value.trim().toLowerCase()
  if (!term) return store.riskItems
  return store.riskItems.filter((item) => item.student_name.toLowerCase().includes(term))
})

const levelColor: Record<RiskLevel, string> = {
  baixo: 'positive',
  medio: 'warning',
  alto: 'negative',
}

const columns = [
  {
    name: 'student_name',
    label: 'Aluno',
    field: 'student_name',
    align: 'left' as const,
    sortable: true,
  },
  { name: 'course_name', label: 'Curso', field: 'course_name', align: 'left' as const },
  {
    name: 'days_inactive',
    label: 'Dias inativo',
    field: 'days_inactive',
    align: 'right' as const,
    sortable: true,
  },
  {
    name: 'submission_rate',
    label: '% entregue',
    field: (row: RiskScoreItem) => `${(row.submission_rate * 100).toFixed(0)}%`,
    align: 'right' as const,
  },
  { name: 'level', label: 'Risco', field: 'level', align: 'center' as const, sortable: true },
  { name: 'actions', label: 'Ações', field: 'actions', align: 'center' as const },
]

const contactDialogOpen = ref(false)
const historyDialogOpen = ref(false)
const activeItem = ref<RiskScoreItem | null>(null)
const contactOutcome = ref<ContactOutcome>('sem_resposta')
const contactNotes = ref('')
const history = ref<ContactLog[]>([])
const saving = ref(false)

function openContactDialog(item: RiskScoreItem) {
  activeItem.value = item
  contactOutcome.value = 'sem_resposta'
  contactNotes.value = ''
  contactDialogOpen.value = true
}

async function openHistoryDialog(item: RiskScoreItem) {
  activeItem.value = item
  history.value = await store.loadContactHistory(item.student_id)
  historyDialogOpen.value = true
}

async function saveContact() {
  if (!activeItem.value) return
  saving.value = true
  try {
    await store.registerContact(activeItem.value.student_id, {
      course_id: activeItem.value.course_id,
      outcome: contactOutcome.value,
      notes: contactNotes.value || undefined,
    })
    contactDialogOpen.value = false
  } finally {
    saving.value = false
  }
}

const outcomeOptions: { label: string; value: ContactOutcome }[] = [
  { label: 'Sem resposta', value: 'sem_resposta' },
  { label: 'Retornou', value: 'retornou' },
  { label: 'Desistiu', value: 'desistiu' },
]

const outcomeLabel: Record<ContactOutcome, string> = {
  sem_resposta: 'Sem resposta',
  retornou: 'Retornou',
  desistiu: 'Desistiu',
}

async function exportCsv() {
  const csv = await store.exportCsv(selectedCourseId.value ?? undefined)
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'lista_priorizada_contato.csv'
  link.click()
  URL.revokeObjectURL(url)
}
</script>

<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md q-gutter-sm">
      <div class="text-h5">Lista priorizada de contato</div>
      <q-space />
      <q-btn color="primary" icon="download" label="Exportar CSV" no-caps @click="exportCsv" />
    </div>

    <div class="row q-col-gutter-sm q-mb-md">
      <div class="col-12 col-sm-4">
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
        />
      </div>
      <div class="col-12 col-sm-4">
        <q-select
          v-model="selectedLevel"
          :options="levelOptions"
          option-label="label"
          option-value="value"
          emit-value
          map-options
          dense
          outlined
          label="Faixa de risco"
        />
      </div>
      <div class="col-12 col-sm-4">
        <q-input v-model="search" dense outlined label="Buscar aluno" clearable>
          <template #prepend><q-icon name="search" /></template>
        </q-input>
      </div>
    </div>

    <q-table
      :rows="filteredItems"
      :columns="columns"
      row-key="enrollment_id"
      :loading="store.loading"
      flat
      bordered
    >
      <template #body-cell-level="props">
        <q-td :props="props">
          <q-badge :color="levelColor[props.row.level as RiskLevel]">
            {{ props.row.level }}
          </q-badge>
        </q-td>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props" class="q-gutter-xs">
          <q-btn
            dense
            flat
            icon="phone"
            :aria-label="`Registrar contato com ${props.row.student_name}`"
            @click="openContactDialog(props.row)"
          />
          <q-btn
            dense
            flat
            icon="history"
            :aria-label="`Ver histórico de ${props.row.student_name}`"
            @click="openHistoryDialog(props.row)"
          />
        </q-td>
      </template>
    </q-table>

    <q-dialog v-model="contactDialogOpen">
      <q-card style="min-width: 320px">
        <q-card-section>
          <div class="text-subtitle1">Registrar contato — {{ activeItem?.student_name }}</div>
        </q-card-section>
        <q-card-section class="q-gutter-md">
          <q-select
            v-model="contactOutcome"
            :options="outcomeOptions"
            option-label="label"
            option-value="value"
            emit-value
            map-options
            outlined
            dense
            label="Resultado"
          />
          <q-input v-model="contactNotes" outlined dense type="textarea" label="Observações" />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn v-close-popup flat label="Cancelar" no-caps />
          <q-btn color="primary" label="Salvar" no-caps :loading="saving" @click="saveContact" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="historyDialogOpen">
      <q-card style="min-width: 320px; max-width: 480px">
        <q-card-section>
          <div class="text-subtitle1">Histórico — {{ activeItem?.student_name }}</div>
        </q-card-section>
        <q-card-section>
          <q-list v-if="history.length" bordered separator>
            <q-item v-for="log in history" :key="log.id">
              <q-item-section>
                <q-item-label>{{ outcomeLabel[log.outcome] }}</q-item-label>
                <q-item-label caption>
                  {{ new Date(log.contacted_at).toLocaleString('pt-BR') }}
                </q-item-label>
                <q-item-label v-if="log.notes" caption>{{ log.notes }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
          <div v-else class="text-grey-7">Nenhum contato registrado ainda.</div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn v-close-popup flat label="Fechar" no-caps />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>
