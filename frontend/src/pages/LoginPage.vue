<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { isDemoMode } from '@/services'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const email = ref(isDemoMode ? 'demo@painelretencao.com' : '')
const password = ref(isDemoMode ? 'demo123456' : '')

async function handleSubmit() {
  const ok = await auth.login(email.value, password.value)
  if (ok) {
    router.push({ name: 'dashboard' })
  }
}
</script>

<template>
  <q-page class="flex flex-center login-page">
    <q-card class="login-card" flat bordered>
      <q-card-section>
        <div class="text-h5 q-mb-xs">Painel de Retenção</div>
        <div class="text-caption text-grey-7">
          Acompanhe o risco de evasão e priorize contatos de tutoria.
        </div>
      </q-card-section>

      <div v-if="isDemoMode" class="demo-notice q-mx-md q-mb-sm" role="status">
        Modo demonstração: dados fictícios, sem backend. Login já preenchido.
      </div>

      <q-card-section>
        <q-form class="q-gutter-md" @submit.prevent="handleSubmit">
          <q-input
            v-model="email"
            type="email"
            label="E-mail"
            autocomplete="username"
            :rules="[(val) => !!val || 'Informe o e-mail']"
          />
          <q-input
            v-model="password"
            type="password"
            label="Senha"
            autocomplete="current-password"
            :rules="[(val) => !!val || 'Informe a senha']"
          />

          <div v-if="auth.error" class="text-negative text-caption" role="alert">
            {{ auth.error }}
          </div>

          <q-btn
            type="submit"
            label="Entrar"
            color="primary"
            class="full-width"
            :loading="auth.loading"
            no-caps
          />
        </q-form>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  padding: 16px;
}

.login-card {
  width: 100%;
  max-width: 420px;
}

.demo-notice {
  background: rgba(37, 99, 235, 0.1);
  color: inherit;
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 0.85rem;
}
</style>
