import { test, expect } from '@playwright/test';

// Basic smoke test: ensure the frontend responds at /
test('Frontend root responds with 200', async ({ page }) => {
  const response = await page.goto('http://localhost:3000');
  expect(response && response.status()).toBe(200);
});
