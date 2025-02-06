import { test, expect } from '@playwright/test';
import { stackURL } from './config'

test('displaying menu : positive', async ({ page }) => {

  await page.goto(stackURL)

  // 1
  //---
  await page.getByRole("button", {name: "Menu"}).click()
  // Allow the menu to slide-in from the left
  await page.waitForTimeout(1500)
  await expect(page).toHaveScreenshot(
    "side-menu.png",
    {clip: {x: 0, y: 0, width: 170, height: 800}},
  )

  // 2
  //---
  await page.getByRole("button", {name: "Home"}).click()
  await expect(page.getByRole("link", {name: "A71EV2A"})).toHaveCount(2);
  await page.getByRole("link", {name: "A71EV2A"}).first().click()
  await page.waitForLoadState("networkidle")
  // By looking at a screenshot of the left-hand side of the 'top-bar',
  // we can verify that the 'NEW PROJECT' button is not present.
  await expect(page).toHaveScreenshot(
    "lh-top-bar.png",
    {clip: {x: 0, y: 0, width: 700, height: 38}},
  )

  // 3
  //---
  await expect(page).toHaveScreenshot("A71EV2A.png")

});
