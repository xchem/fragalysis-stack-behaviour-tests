import { test, expect } from '@playwright/test';
import { stackURL } from './config'

test('displaying menu : positive', async ({ page }) => {

  await page.goto(stackURL)

  // 1
  //---
  await page.getByRole("button", {name: "Menu"}).click()
  // Allow the menu to slide-in from the left
  await page.waitForTimeout(1500)
  expect(await page.screenshot({clip: {x: 0, y: 0, width: 170, height: 1080}}))
    .toMatchSnapshot("side-menu.png")

  // 2
  //---
  await page.getByRole("button", {name: "Home"}).click()
  await expect(page.getByRole("link", {name: "A71EV2A"})).toHaveCount(2);
  await page.getByRole("link", {name: "A71EV2A"}).first().click()
  await page.waitForLoadState("networkidle")
  // By looking at a screenshot of the left-hand side of the 'top-bar',
  // we can verify that the 'NEW PROJECT' button is not present.
  expect(await page.screenshot({clip: {x: 0, y: 0, width: 700, height: 42}}))
    .toMatchSnapshot("lh-top-bar.png")

  // 3
  //---
  expect(await page.screenshot())
    .toMatchSnapshot("target-view-A71EV2A.png")

});
