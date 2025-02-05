import { test, expect } from '@playwright/test';

const stackHostname = process.env.STACK_HOSTNAME
const stackUsername = process.env.STACK_USERNAME
const stackPassword = process.env.STACK_PASSWORD

test('login', async ({ page }) => {

  // 1
  await page.goto(`https://${stackHostname}/`)
  await page.getByRole("button", {name: "Menu"}).click()
  await page.getByRole("button", {name: "Login"}).click()

  // 2
  await page.getByRole("link", {name: "Diamond CAS"}).click()
  await page.getByRole("textbox", {name: "Username:"}).fill(`${stackUsername}`)
  await page.getByRole("textbox", {name: "Password:"}).fill(`${stackPassword}`)
  await page.getByRole("button", {name: "Login"}).click()
  await expect(page.getByText("You're logged in")).toBeVisible()

});
