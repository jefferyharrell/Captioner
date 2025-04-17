import { test, expect } from '@playwright/test';

// This test assumes the backend is running and contains at least two photos.
test('Clicking Next fetches a new random photo', async ({ page, request }) => {
  // Get two different random photos from the backend
  const resp1 = await request.get('http://localhost:8000/photos/random');
  expect(resp1.ok()).toBeTruthy();
  const photo1 = await resp1.json();

  let photo2;
  for (let i = 0; i < 5; i++) {
    const resp2 = await request.get('http://localhost:8000/photos/random');
    expect(resp2.ok()).toBeTruthy();
    photo2 = await resp2.json();
    if (photo2.hash !== photo1.hash) break;
  }
  expect(photo2.hash).not.toBe(photo1.hash);

  // Intercept the first random-photo fetch with photo1, then the next with photo2
  let callCount = 0;
  await page.route('**/photos/random', async route => {
    callCount++;
    if (callCount === 1) {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(photo1) });
    } else {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(photo2) });
    }
  });

  // Visit the frontend and wait for the first photo
  await page.goto('http://localhost:3000');
  await expect(page.getByAltText(photo1.filename)).toBeVisible();
  await expect(page.getByText(`Filename: ${photo1.filename}`)).toBeVisible();

  // Click the Next button
  const nextButton = page.getByLabel('Next random photo');
  await nextButton.click();

  // Wait for the new photo to appear
  await expect(page.getByAltText(photo2.filename)).toBeVisible();
  await expect(page.getByText(`Filename: ${photo2.filename}`)).toBeVisible();
});
