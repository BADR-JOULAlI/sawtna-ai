import { defineConfig } from '@playwright/test'

// Isolated citizen UI checks. Fixtures never enter the application bundle.
export default defineConfig({
  testDir: './tests', testMatch: 'citizen.spec.js', timeout: 30000,
  fullyParallel: false, workers: 1,
  reporter: [['list'], ['json', { outputFile: 'test-results/citizen-results.json' }]],
  use: {
    baseURL: 'http://127.0.0.1:5185', viewport: { width: 1280, height: 960 },
    channel: process.env.SAWTNA_BROWSER_CHANNEL || undefined,
    screenshot: 'only-on-failure', trace: 'retain-on-failure',
  },
  webServer: {
    command: 'npm run dev -- --port 5185', url: 'http://127.0.0.1:5185',
    reuseExistingServer: false, env: { VITE_API_BASE_URL: '' },
  },
})
