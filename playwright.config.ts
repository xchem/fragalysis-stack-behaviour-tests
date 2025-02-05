import { defineConfig, devices } from '@playwright/test';

// Read environment variables from file.
// https://github.com/motdotla/dotenv
import dotenv from 'dotenv';
import path from 'path';
dotenv.config({ path: path.resolve(__dirname, '.env') });

// See https://playwright.dev/docs/test-configuration.
export default defineConfig({

  testDir: './playwright',
  fullyParallel: false,

  // Fail the build on CI if you accidentally left test.only in the source code.
  forbidOnly: !!process.env.CI,
  // Retries on CI?
  retries: process.env.CI ? 1 : 0,
  // Opt out of parallel tests on CI.
  workers: process.env.CI ? 1 : undefined,

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
      use: { ...devices['Desktop Chrome'], channel: 'chrome' },
    },
  ],

  // Assertion-specific templates
  expect: {
    toHaveScreenshot: {
      pathTemplate: '{testDir}/Screenshots/{testFilePath}/{arg}{ext}',
    },
  },
});
