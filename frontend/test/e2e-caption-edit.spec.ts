import { test, expect } from '@playwright/test';

// This test assumes the backend is running and contains at least one photo.
test('Editing a caption in the frontend updates the backend database', async ({ page, request }) => {
  // Step 0: Get a known photo from backend DB
  const randomPhotoResp = await request.get('http://localhost:8000/photos/random');
  expect(randomPhotoResp.ok()).toBeTruthy();
  const photo = await randomPhotoResp.json();
  const newCaption = `Test caption ${Date.now()}`;

  // Intercept frontend's random-photo fetch so it uses our photo
  await page.route('**/photos/random', async route => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(photo) });
  });

  // Step 2: Visit the frontend and wait for the photo to load
  await page.goto('http://localhost:3000');
  await expect(page.getByAltText(photo.filename)).toBeVisible();

  // Step 3: Edit the caption in the input field
  const input = page.getByPlaceholder('Enter a caption…');
  await input.fill(newCaption);

  // Step 4: Click the save button
  await page.getByRole('button', { name: /Save Caption/i }).click();

  // Step 5: Wait for the UI to reflect the new caption
  await expect(input).toHaveValue(newCaption);

  // Step 6: Fetch the photo again from the backend and verify the caption is updated
  const updatedResp = await request.get(`http://localhost:8000/photos/${photo.hash}`);
  expect(updatedResp.ok()).toBeTruthy();
  const updated = await updatedResp.json();
  expect(updated.caption).toBe(newCaption);
});
