# playwright
This directory contains the [Playwright] tests for the project.
The initial set of tests, started in early 2025, are based on the written
TestLink Execution Report ("Regression Test 4: dated 14 Nov 2024). The tests
are manual tests and form a suitable base from which to build an automated
suite of tests.

We have chosen to use Playwright, an extremely powerful UI testing
framework, and a de-facto standard for testing web applications. The test
are written using [TypeScript], the natural language of Playwright.

## Style guide
And dynamic control variables (configuration) for the tests **MUST** be extracted
from environment variables in `config.ts`, and exported/imported as needed.

Test fixtures **MUST*** defined in individual files using a filename with the prefix
`test-fixture-`. Test fixyures **SHOULD** have their own test files, where that file
uses a prefix of `test-fixture-<fixture name>-.spec.ts`.

Tests that replicate the manual tests of the TestLink Execution Report **MUST**
be found in a file whose name is `testlink-<NNN>.spec.ts`, where `<NNN>` is the
TestLink *Oxford* test case number.

Each file should start with a brief JSDoc comment that confirms the origin of the
test (for TestLink tests). For example *M2MS TestLink Test Case Oxford-1 (14 Nov 2024)*.

Tests for TestLink tests must be structured clearly to identify the test step number
from the original document, for example step 1 would use a number and a line comment,
and a clear separator like `//---`: -

    // 1
    //---
    await page.goto(stackURL)
    await page.getByRole("button", {name: "Menu"}).click()
    [...]

One test, one file.

## Debugging the Playwright (UI) tests
You can do a lot of debugging using the built-in UI/browser: -

    npx playwright test --ui

You can also investigate CI failures by downloading the **playwright-report** artifact,
unpack it, and then run `show-report`, naming the unpacked directory.
This will allow you to inspect the failures including comparing screen snapshots
(this is a really cool feature!): -

    npx playwright show-report ~/Downloads/playwright-report

---

[playwright]: https://playwright.dev
[typescript]: https://www.typescriptlang.org
