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

test('manual image without an AI service names no recipient and can be removed', async ({page}) => {
  await page.goto('/');
  await page.getByRole('button',{name:'Preview first-time setup',exact:true}).click();
  await page.setViewportSize({width:360,height:720});
  const panel = page.locator('aside');
  await panel.getByRole('button',{name:'Game',exact:true}).click();
  await panel.getByLabel('Game title').fill('Test');
  await panel.getByLabel('What are you trying to do?').fill('prova');
  await panel.getByRole('button',{name:'Save game',exact:true}).click();
  await panel.getByRole('button',{name:'Settings',exact:true}).click();
  await expect(panel.getByRole('combobox',{name:/^AI service/})).toHaveValue('');
  await panel.getByLabel(/Allow adding game images/).check();
  await panel.getByRole('button',{name:'Save settings',exact:true}).click();
  await panel.getByRole('button',{name:'Play',exact:true}).click();
  await expect(panel.getByText('Test',{exact:true})).toBeVisible();
  const png = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aF9sAAAAASUVORK5CYII=', 'base64');
  await panel.getByLabel('Game image file').setInputFiles({name:'deckpilot-synthetic-test.png', mimeType:'image/png', buffer:png});
  await expect(panel.getByAltText('Image to be shared, with metadata removed')).toBeVisible();
  await expect(panel.getByText(/^No AI service chosen yet\./)).toBeVisible();
  await expect(panel).not.toContainText('{provider}');
  await expect(panel.getByRole('button',{name:'Allow this image to be shared',exact:true})).toBeDisabled();
  await expect(panel.getByRole('button',{name:'Help me now',exact:true})).toBeDisabled();
  expect(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)).toBe(false);
  await panel.locator('.dp-card', {has: page.getByAltText('Image to be shared, with metadata removed')}).screenshot({path:'artifacts/preview-manual-image-no-recipient.png'});
  // Keyboard/D-pad style traversal reaches the remove action without a pointer.
  await panel.getByRole('button',{name:'Remove image',exact:true}).focus();
  await page.keyboard.press('Enter');
  await expect(panel.getByAltText('Image to be shared, with metadata removed')).toHaveCount(0);
});

test('prepared image survives the panel being removed while the file picker is open', async ({page}) => {
  const errors: string[] = []; page.on('pageerror', error => errors.push(error.message));
  await page.goto('/?picker=1');
  await page.getByRole('button',{name:'Preview first-time setup',exact:true}).click();
  await page.getByRole('button',{name:'Game',exact:true}).click();
  await page.getByLabel('Game title').fill('Test');
  await page.getByLabel('What are you trying to do?').fill('prova');
  await page.getByRole('button',{name:'Save game',exact:true}).click();
  await page.getByRole('button',{name:'Settings',exact:true}).click();
  await page.getByLabel(/Allow adding game images/).check();
  await page.getByRole('button',{name:'Save settings',exact:true}).click();
  await page.getByRole('button',{name:'Play',exact:true}).click();
  await page.getByRole('button',{name:'Add game image',exact:true}).click();
  // The whole panel is gone from the document, as observed in the real Quick Access.
  await expect(page.getByRole('dialog',{name:'Simulated file picker'})).toBeVisible();
  await expect(page.locator('aside')).toHaveCount(0);
  await page.getByRole('button',{name:'Select this file',exact:true}).click();
  await expect(page.getByAltText('Image to be shared, with metadata removed')).toBeVisible();
  await expect(page.getByText(/^No AI service chosen yet\./)).toBeVisible();
  await expect(page.getByRole('alert')).toHaveCount(0);
  await page.getByRole('button',{name:'Remove image',exact:true}).click();
  await expect(page.getByAltText('Image to be shared, with metadata removed')).toHaveCount(0);
  expect(errors).toEqual([]);
});

// Quick Access column: 300px wide with a 56px icon rail on the left, as in the real sidebar.
test('panel stays inside a narrow Quick Access column', async ({page}) => {
  await page.setViewportSize({width:1280,height:800});
  await page.goto('/?picker=1&qam=1');
  const overflow = () => page.evaluate(() => {
    const aside = document.querySelector('aside')!.getBoundingClientRect();
    const left = aside.left + 56, right = aside.right, bad: string[] = [];
    for (const el of document.querySelectorAll<HTMLElement>('aside .dp *')) {
      const r = el.getBoundingClientRect();
      if (!r.width || el.closest('.dp-scroll') === null && el.tagName === 'STYLE') continue;
      // Glyph boxes, not scrollWidth: centred button text overflows on both sides and is not counted there.
      const range = document.createRange(); range.selectNodeContents(el);
      const text = range.getBoundingClientRect();
      if (text.width && (text.left < r.left - 1 || text.right > r.right + 1) && el.querySelector('*') === null) bad.push(`text overflows ${el.tagName}:${(el.textContent ?? '').slice(0, 20)}`);
      if (r.left < left - 1 || r.right > right + 1) bad.push(`${el.tagName}.${el.className}:${(el.textContent ?? '').slice(0, 20)} ${Math.round(r.left - left)}/${Math.round(r.right - right)}`);
    }
    const scroll = document.querySelector<HTMLElement>('aside .dp-scroll')!;
    return {bad, wide: scroll.scrollWidth > scroll.clientWidth};
  });
  for (const label of ['Game', 'Settings', 'Play']) {
    await page.getByRole('button',{name:label,exact:true}).click();
    const result = await overflow();
    expect(result, label).toEqual({bad: [], wide: false});
  }
  await page.getByRole('button',{name:'Settings',exact:true}).click();
  await page.getByLabel('Interface language').selectOption('it');
  for (const label of ['Gioco', 'Impostazioni', 'Gioca']) {
    await page.getByRole('button',{name:label,exact:true}).click();
    expect(await overflow(), label).toEqual({bad: [], wide: false});
  }
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
