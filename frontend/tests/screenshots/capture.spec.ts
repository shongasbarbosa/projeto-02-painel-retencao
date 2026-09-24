import path from 'node:path'
import { fileURLToPath } from 'node:url'

import { expect, test } from '@playwright/test'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const SHOTS_DIR = path.resolve(__dirname, '../../../docs/screenshots')

async function login(page: import('@playwright/test').Page) {
  await page.goto('/#/login')
  await page.getByRole('button', { name: 'Entrar' }).click()
  await expect(page.getByRole('main').getByText('Dashboard')).toBeVisible()
}

test.describe('Painel de Retenção — screenshots (modo demo)', () => {
  test('login', async ({ page }) => {
    await page.goto('/#/login')
    await expect(page.getByText('Modo demonstração')).toBeVisible()
    await page.screenshot({ path: `${SHOTS_DIR}/01-login.png` })
  })

  test('dashboard desktop (claro)', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 800 })
    await login(page)
    await page.waitForTimeout(500) // aguarda renderização dos gráficos ECharts
    await page.screenshot({ path: `${SHOTS_DIR}/02-dashboard-desktop-claro.png`, fullPage: true })
  })

  test('dashboard mobile (360px)', async ({ page }) => {
    await page.setViewportSize({ width: 360, height: 780 })
    await login(page)
    await page.waitForTimeout(500)
    await page.screenshot({ path: `${SHOTS_DIR}/03-dashboard-mobile.png`, fullPage: true })
  })

  test('lista de contato com diálogo aberto', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 800 })
    await login(page)
    await page.getByRole('tab', { name: 'Contato' }).first().click()
    await page.waitForSelector('table tbody tr')
    await page
      .getByRole('button', { name: /Registrar contato com/ })
      .first()
      .click()
    await expect(page.getByText('Registrar contato —')).toBeVisible()
    await page.screenshot({ path: `${SHOTS_DIR}/04-contato-dialogo.png` })
  })

  test('comparação entre turmas', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 800 })
    await login(page)
    await page.getByRole('tab', { name: 'Comparação' }).first().click()
    await page.waitForTimeout(500)
    await page.screenshot({ path: `${SHOTS_DIR}/05-comparacao.png`, fullPage: true })
  })

  test('dashboard em tema escuro e cabeçalho com seletor de tema', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 800 })
    await login(page)
    await page.getByRole('button', { name: 'Escuro' }).click()
    await page.waitForTimeout(400)
    await page.screenshot({ path: `${SHOTS_DIR}/06-dashboard-escuro.png`, fullPage: true })
    await page.locator('.q-header').screenshot({ path: `${SHOTS_DIR}/07-cabecalho-tema.png` })
  })
})
