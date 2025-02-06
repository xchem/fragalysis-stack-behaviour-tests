import { defineConfig, devices } from '@playwright/test';

// See https://playwright.dev/docs/test-configuration.
export default defineConfig({

  testDir: './playwright',
  fullyParallel: false,
  timeout: 600_000,

  // Fail the build on CI if you accidentally left test.only in the source code.
  forbidOnly: !!process.env.CI,
  // Retries on CI?
  retries: process.env.CI ? 1 : 0,
  // Opt out of parallel tests on CI.
  workers: process.env.CI ? 1 : 1,

  reporter: 'html',

  // Shared settings for all the projects below.
  // See https://playwright.dev/docs/api/class-testoptions.
  use: {
    // Collect trace when retrying the failed test.
    // See https://playwright.dev/docs/trace-viewer
    trace: 'on-first-retry',
  },

  // Configure projects for chrome-only
  // The only supported browser (atm)
  projects: [
    {
      name: 'Google Chrome',
      use: {
        ...devices['Desktop Chrome'],
        channel: 'chrome',
        // Full HD resolution...
        viewport: {width: 1920, height: 1080},
      },
    },
  ],

  // Assertion-specific templates
  expect: {
    timeout: 5_000,
    toHaveScreenshot: {
      pathTemplate: '{testDir}/Screenshots/{testFilePath}/{arg}{ext}',
      maxDiffPixels: 50,
    },
    toMatchSnapshot: {
      maxDiffPixelRatio: 0.1,
    },
  },
});
