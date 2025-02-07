import { defineConfig, devices } from '@playwright/test';

// See https://playwright.dev/docs/test-configuration.
export default defineConfig({

  testDir: './playwright',
  fullyParallel: false,
  timeout: 600_000,

  // Fail the build on CI if you accidentally left test.only in the source code.
  forbidOnly: !!process.env.CI,
  retries: 1,
  // Opt out of parallel tests
  workers: 1,
  reporter: 'html',
  // Path template for snapshot files.
  // At the moment we remove the browser and platform from the path
  // and put everything into a Snapshots directory.
  snapshotPathTemplate: '{testDir}/Snapshots/{testFilePath}/{arg}{ext}',

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
    timeout: 2_000,
    toMatchSnapshot: {
      maxDiffPixelRatio: 0.08,
    },
  },

});
