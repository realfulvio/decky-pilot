import { expect, test } from '@playwright/test';
for (const height of [800, 720]) {
  test(`English preview chat, focus and layout 1280x${height}`, async ({page}) => {
    await page.setViewportSize({width: 1280, height});
    const errors: string[] = []; page.on('pageerror', error => errors.push(error.message));
    await page.goto('/');
    await expect(page.getByText('OFFLINE PREVIEW · sample data, no AI calls or device capture')).toBeVisible();
    await expect(page.getByRole('button', {name: 'Help me now', exact: true})).toBeVisible();
    await page.getByLabel('Ask a question').fill('Which symbol should I choose?');
    await page.getByRole('button', {name: 'Ask Decky Pilot', exact: true}).click();
    await expect(page.getByText('Look at the symbol on the door. If a detail is missing, describe it.', {exact: true})).toBeVisible();
    await page.getByRole('button', {name: 'Game', exact: true}).click();
    await page.getByLabel('Game title').fill('Sample non-Steam game');
    await page.getByRole('button', {name: 'Save game', exact: true}).click();
    await page.getByRole('button', {name: 'Play', exact: true}).click();
    await expect(page.getByText('Sample non-Steam game', {exact: true})).toBeVisible();
    await page.getByLabel('Ask a question').fill('A follow-up question');
    await page.getByLabel('Ask a question').focus();
    await page.keyboard.press('Tab');
    await expect(page.getByRole('button', {name: 'Ask Decky Pilot', exact: true})).toBeFocused();
    await page.getByRole('button', {name: 'Stop', exact: true}).scrollIntoViewIfNeeded();
    await expect(page.getByRole('button', {name: 'Stop', exact: true})).toBeVisible();
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
  await expect(page.getByLabel('Lingua dell’assistente (risposte e voce)')).toHaveValue('en');
  await expect(page.getByLabel('Lingua dell’assistente (risposte e voce)')).toBeVisible();
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

for (const height of [800,720]) {
  test(`narrow quick-access preview, branding and usable controls 360x${height}`, async ({page}) => {
    await page.setViewportSize({width:360,height}); await page.goto('/');
    await expect(page.getByRole('button',{name:'Help me now',exact:true})).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)).toBe(false);
    await page.getByRole('button',{name:'Stop',exact:true}).scrollIntoViewIfNeeded();
    await expect(page.getByRole('button',{name:'Stop',exact:true})).toBeVisible();
    await page.screenshot({path:`artifacts/preview-narrow-360x${height}.png`});
    await page.setViewportSize({width:1280,height});
    await page.getByRole('button',{name:'Preview first-time setup',exact:true}).click();
    await page.setViewportSize({width:360,height});
    await expect(page.getByRole('img',{name:'Decky Pilot',exact:true}).last()).toBeVisible();
    await page.getByRole('button',{name:'Get started',exact:true}).scrollIntoViewIfNeeded();
    await expect(page.getByRole('button',{name:'Get started',exact:true})).toBeVisible();
    // The same hand-drawn menu SVG used in src/index.tsx, at actual small sizes.
    await page.evaluate(() => {
      const icon = document.querySelector('aside .dp img') as HTMLImageElement;
      const row=document.createElement('div'); row.id='icon-size-check';
      row.style.cssText='position:fixed;top:0;left:0;background:#0B1320;padding:4px';
      for (const size of [20,24,32]) {const copy=icon.cloneNode() as HTMLImageElement;copy.width=size;copy.height=size;row.append(copy);}
      document.body.append(row);
    });
    await page.locator('#icon-size-check').screenshot({path:`artifacts/menu-icon-sizes-${height}.png`});
  });
}
