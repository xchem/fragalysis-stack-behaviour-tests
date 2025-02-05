import { test, expect } from '@playwright/test';

const stackHostname = process.env.STACK_HOSTNAME

test('login', async ({ page }) => {

  // 1
  await page.goto(`https://${stackHostname}/`)
  await page.getByRole("button", {name: "Menu"}).click()
  // Let the menu slide-in from the left
  await page.waitForTimeout(2000)
  await expect(page).toHaveScreenshot(
    "menu.png",
    {
      clip: {x: 0, y: 0, width: 170, height: 800},
      maxDiffPixels: 10,
    }
  )

});
