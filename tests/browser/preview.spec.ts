import { expect, test } from '@playwright/test';
for (const height of [800, 720]) {
  test(`English preview chat, focus and layout 1280x${height}`, async ({page}) => {
    await page.setViewportSize({width: 1280, height});
    const errors: string[] = []; page.on('pageerror', error => errors.push(error.message));
    await page.goto('/');
    await expect(page.getByText('OFFLINE PREVIEW · sample data, no AI calls or device capture')).toBeVisible();
    await expect(page.getByRole('button', {name: 'Help me now', exact: true})).toBeVisible();
    await page.getByLabel('Or ask a question').fill('Which symbol should I choose?');
    await page.getByRole('button', {name: 'Ask DeckPilot', exact: true}).click();
    await expect(page.getByText('Look at the symbol on the door. If a detail is missing, describe it.', {exact: true})).toBeVisible();
    await page.getByRole('button', {name: 'Game', exact: true}).click();
    await page.getByLabel('Game title').fill('Sample non-Steam game');
    await page.getByRole('button', {name: 'Save game', exact: true}).click();
    await page.getByRole('button', {name: 'Play', exact: true}).click();
    await expect(page.getByText('Sample non-Steam game', {exact: true})).toBeVisible();
    await page.getByLabel('Or ask a question').fill('A follow-up question');
    await page.getByLabel('Or ask a question').focus();
    await page.keyboard.press('Tab');
    await expect(page.getByRole('button', {name: 'Ask DeckPilot', exact: true})).toBeFocused();
    await page.getByRole('button', {name: 'Stop voice', exact: true}).scrollIntoViewIfNeeded();
    await expect(page.getByRole('button', {name: 'Stop voice', exact: true})).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)).toBe(false);
    await page.getByRole('button', {name: 'Help me now', exact: true}).scrollIntoViewIfNeeded();
    await page.screenshot({path: `artifacts/preview-1280x${height}.png`});
    expect(errors).toEqual([]);
  });
}

test('Italian UI keeps AI and voice defaults English', async ({page}) => {
  await page.goto('/');
  await page.getByRole('button', {name: 'Settings', exact: true}).click();
  await page.getByLabel('Interface language').selectOption('it');
  await expect(page.getByLabel('Lingua delle risposte AI')).toHaveValue('en');
  await expect(page.getByLabel('Lingua della voce')).toHaveValue('en');
  await page.getByRole('button', {name: 'Gioca', exact: true}).click();
  await expect(page.getByRole('button', {name: 'Aiutami ora', exact: true})).toBeVisible();
  await page.screenshot({path: 'artifacts/preview-italian.png'});
});

test('image review shows destination and sends only after approval', async ({page}) => {
  await page.goto('/');
  // Synthetic PNG with no private gameplay or account data.
  const png = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aF9sAAAAASUVORK5CYII=', 'base64');
  await page.getByLabel('Game image file').setInputFiles({name:'sample.png', mimeType:'image/png', buffer:png});
  await expect(page.getByAltText('Image to be shared, with metadata removed')).toBeVisible();
  await expect(page.getByRole('button', {name:'Help me now',exact:true})).toBeDisabled();
  await page.getByRole('button', {name:'Allow this image to be shared',exact:true}).click();
  await expect(page.getByRole('button', {name:'Help me now',exact:true})).toBeEnabled();
  await page.getByRole('button', {name:'Help me now',exact:true}).click();
  await expect(page.getByText('Look at the symbol on the door. If a detail is missing, describe it.', {exact:true})).toBeVisible();
});
