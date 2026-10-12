import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: 'tests/browser', timeout: 30000, retries: 0, workers: 1,
  use: {baseURL: 'http://127.0.0.1:5173', browserName: 'chromium', channel: process.env.PLAYWRIGHT_CHANNEL === 'chromium' ? undefined : 'msedge'},
  webServer: {command: 'corepack pnpm preview', url: 'http://127.0.0.1:5173', reuseExistingServer: false, timeout: 30000}
});
