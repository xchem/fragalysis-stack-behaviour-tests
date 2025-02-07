/**
 * Test the login fixture.
 */
import { test } from './fixture-login'

test('/accounts/login', async ({ loggedInPage }) => {

  await loggedInPage.getByRole("button", {name: "Menu"}).click()

});
