import { expect, test } from '@playwright/test';
for (const height of [800, 720]) {
  test(`harness offline chat/focus/layout 1280x${height}`, async ({page}) => {
    await page.setViewportSize({width: 1280, height});
    const errors: string[] = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto('/');
    await expect(page.getByText('HARNESS OFFLINE · risposte sintetiche, nessuna API o dispositivo')).toBeVisible();
    await page.getByLabel('Domanda (massimo 4.000 caratteri)').fill('Quale simbolo devo scegliere?');
    await page.getByRole('button', {name: 'Chiedi', exact: true}).click();
    await expect(page.getByRole('log')).toContainText('Controlla il simbolo sulla porta.');
    await page.getByRole('button', {name: 'Contesto del gioco', exact: true}).click();
    await page.getByLabel('Titolo del gioco').fill('Gioco sintetico non Steam');
    await page.getByRole('button', {name: 'Salva contesto manuale', exact: true}).click();
    await expect(page.getByText(/Gioco sintetico non Steam ·/)).toBeVisible();
    await page.getByRole('button', {name: 'Chat', exact: true}).click();
    await page.getByLabel('Domanda (massimo 4.000 caratteri)').focus();
    await page.keyboard.press('Tab');
    await expect(page.getByRole('button', {name: 'Scegli immagine PNG/JPEG', exact: true})).toBeFocused();
    await expect(page.getByRole('button', {name: 'Interrompi voce', exact: true})).toBeVisible();
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth);
    expect(overflow).toBe(false);
    await page.screenshot({path: `artifacts/preview-1280x${height}.png`});
    expect(errors).toEqual([]);
  });
}
