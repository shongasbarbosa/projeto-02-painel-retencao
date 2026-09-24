import { defineConfig, devices } from '@playwright/test'

// Config separada dos screenshots: roda os fluxos de autenticação tanto no
// modo demonstração (build estático) quanto contra a API real (esperada
// rodando via `docker compose up`, ex.: frontend em localhost:8080).
export default defineConfig({
  testDir: './tests/e2e',
  timeout: 30_000,
  fullyParallel: false,
  workers: 1,
  reporter: [['list']],
  webServer: {
    command: 'npm run build -- --mode demo && npx vite preview --mode demo --port 4176',
    url: 'http://localhost:4176',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
  projects: [
    {
      name: 'demo-mode',
      use: { ...devices['Desktop Chrome'], baseURL: 'http://localhost:4176' },
    },
    {
      name: 'real-api',
      // Requer `docker compose up` rodando (frontend servido em localhost:8080).
      use: { ...devices['Desktop Chrome'], baseURL: 'http://localhost:8080' },
    },
  ],
})
