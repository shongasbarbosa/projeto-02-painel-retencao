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
      <q-card-section class="login-card__section">
        <div class="login-card__header">
          <div class="text-h5">Painel de Retenção</div>
          <div class="text-caption text-grey-7">
            Acompanhe o risco de evasão e priorize contatos de tutoria.
          </div>
        </div>

        <div v-if="isDemoMode" class="demo-notice" role="status">
          Modo demonstração: dados fictícios, sem backend. Login já preenchido.
        </div>

        <q-form class="login-card__form" @submit.prevent="handleSubmit">
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
            class="full-width login-card__submit"
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

.login-card__section {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 28px 24px;
}

.login-card__header {
  display: flex;
  flex-direction: column;
  gap: 4px;
  text-align: center;
}

.login-card__form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.login-card__submit {
  margin-top: 4px;
}

.demo-notice {
  background: rgba(37, 99, 235, 0.1);
  color: inherit;
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 0.85rem;
  text-align: center;
}
</style>
