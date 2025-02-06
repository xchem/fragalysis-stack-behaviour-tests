import { test, expect } from '@playwright/test';
import { stackURL, stackUsername, stackPassword } from './config'

test('login : positive', async ({ page }) => {

  await page.goto(stackURL)

  // 1
  //---
  await page.getByRole("button", {name: "Menu"}).click()
  await page.getByRole("button", {name: "Login"}).click()

  // 2
  //---
  await page.getByRole("link", {name: "Diamond CAS"}).click()
  await page.getByRole("textbox", {name: "Username:"}).fill(`${stackUsername}`)
  await page.getByRole("textbox", {name: "Password:"}).fill(`${stackPassword}`)
  await page.getByRole("button", {name: "Login"}).click()
  expect(page.getByText("You're logged in")).toBeVisible()
  await page.getByRole("button", {name: /close/i}).click()

});
