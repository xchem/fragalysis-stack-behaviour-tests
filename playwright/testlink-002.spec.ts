/**
 * M2MS TestLink Test Case Oxford-2 (14 Nov 2024)
 *
 * Note: This test case uses the App Menu/Login rather than the login fixture.
 */
import { test, expect } from '@playwright/test';
import { stackURL, stackUsername, stackPassword } from './config'

test('login', async ({ page }) => {

  // 1
  //---
  await page.goto(stackURL)
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
