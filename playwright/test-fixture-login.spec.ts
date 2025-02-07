/**
 * A test that simply ensures the login fixture is working.
 */
import { test } from './fixture-login'

test('/accounts/login', async ({ loggedInPage }) => {

  await loggedInPage.getByRole("button", {name: "Menu"}).click()

});
