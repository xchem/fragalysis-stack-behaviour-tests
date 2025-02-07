/**
 * A test fixture that navigates to the login endpoint of Fragalysis
 * and logs in via the CAS authenticator. This *DOES NOT* use the Menu/Login
 * feature of the application, which is verified by test 'testlink-002'.
 * Instead, this fixture is used by any test that starts, *assuming* the user is
 * logged in.
 */
import {test as baseTest} from '@playwright/test';
import {stackURL, stackUsername, stackPassword} from './config'

const test = baseTest.extend<{loggedInPage: any}> ({

  loggedInPage : async({ page }, use) => {

    // Goto the login page
    await page.goto(`${stackURL}/accounts/login`)
    // fill-in login details
    await page.getByRole("link", {name: "Diamond CAS"}).click()
    await page.getByRole("textbox", {name: "Username:"}).fill(`${stackUsername}`)
    await page.getByRole("textbox", {name: "Password:"}).fill(`${stackPassword}`)
    await page.getByRole("button", {name: "Login"}).click()
    // Make the logged-in page available for tests
    await use(page);

  }

})

export { test };
