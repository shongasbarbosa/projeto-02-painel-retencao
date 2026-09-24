<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

import ThemeToggle from '@/components/ThemeToggle.vue'
import { isDemoMode } from '@/services'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()

const showHeader = computed(() => route.name !== 'login')

function handleLogout() {
  auth.logout()
}
</script>

<template>
  <q-layout view="hHh lpR fFf">
    <q-header v-if="showHeader" elevated>
      <q-toolbar>
        <q-toolbar-title>
          <router-link to="/" class="header-link">Painel de Retenção</router-link>
        </q-toolbar-title>

        <q-tabs class="gt-xs" indicator-color="white">
          <q-route-tab to="/" label="Dashboard" />
          <q-route-tab to="/contatos" label="Contato" />
          <q-route-tab to="/comparacao" label="Comparação" />
        </q-tabs>

        <ThemeToggle class="q-mx-sm" />

        <q-btn flat round icon="logout" aria-label="Sair" @click="handleLogout" />
      </q-toolbar>

      <q-tabs class="lt-sm" indicator-color="white">
        <q-route-tab to="/" label="Dashboard" />
        <q-route-tab to="/contatos" label="Contato" />
        <q-route-tab to="/comparacao" label="Comparação" />
      </q-tabs>

      <div v-if="isDemoMode" class="demo-banner" role="status">
        Modo demonstração: dados fictícios, sem backend
      </div>
    </q-header>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<style scoped>
.header-link {
  color: inherit;
  text-decoration: none;
}

.demo-banner {
  background: var(--q-warning);
  color: #1a1a1a;
  text-align: center;
  font-size: 0.85rem;
  padding: 4px 8px;
}
</style>
