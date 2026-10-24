import { defineConfig } from '@playwright/test';
export default defineConfig({
  timeout: 120000,
  testDir: './browser-tests',
  use: {
    baseURL: 'http://127.0.0.1:4173/Personal-Website/',
    // Software WebGL so the 3D island also runs headless.
    launchOptions: {
      args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'],
      ...(process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH
        ? { executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH }
        : {}),
    },
  },
  webServer: { command: 'npm run dev -- --port 4173', url: 'http://127.0.0.1:4173/Personal-Website/', reuseExistingServer: !process.env.CI },
});
