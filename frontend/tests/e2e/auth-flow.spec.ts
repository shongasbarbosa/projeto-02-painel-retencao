import { expect, test } from '@playwright/test'

test.describe('Fluxo de autenticação (login e logout)', () => {
  test('faz login, navega e desconecta voltando para a tela de login', async ({ page }) => {
    await page.goto('/#/login')
    await expect(page.getByText('Painel de Retenção').first()).toBeVisible()

    await page.fill('input[type="email"]', 'demo@painelretencao.com')
    await page.fill('input[type="password"]', 'demo123456')
    await page.getByRole('button', { name: 'Entrar' }).click()

    await expect(page.getByRole('main').getByText('Dashboard')).toBeVisible()
    expect(page.url()).toContain('/#/')
    expect(page.url()).not.toContain('/#/login')

    await page.getByRole('tab', { name: 'Contato' }).first().click()
    await expect(page.getByRole('main').getByText('Lista priorizada de contato')).toBeVisible()

    await page.getByRole('button', { name: 'Sair' }).click()

    await expect(page).toHaveURL(/#\/login$/)
    await expect(page.getByRole('button', { name: 'Entrar' })).toBeVisible()

    // O botão "voltar" do navegador não deve levar a uma tela protegida.
    await page.goBack()
    await expect(page).toHaveURL(/#\/login$/)
    await expect(page.getByRole('button', { name: 'Entrar' })).toBeVisible()
  })

  test('rota protegida redireciona para o login quando não autenticado', async ({ page }) => {
    await page.goto('/#/contatos')
    await expect(page).toHaveURL(/#\/login$/)
  })
})
