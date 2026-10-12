// Anonymous browser verification of the actual published GitHub presentation.
import {chromium} from '@playwright/test';
import {mkdir} from 'node:fs/promises';
await mkdir('artifacts/github-public', {recursive:true});
const browser = await chromium.launch({channel:process.env.PLAYWRIGHT_CHANNEL === 'chromium' ? undefined : 'msedge'});
try {
  for (const [name, url] of [
    ['English','https://github.com/realfulvio/decky-pilot'],
    ['Italian','https://github.com/realfulvio/decky-pilot/blob/main/README.it.md']
  ]) {
    for (const width of [1200,390]) {
      const page = await browser.newPage({viewport:{width,height:900}});
      const response = await page.goto(`${url}?presentationVerification=${Date.now()}`, {waitUntil:'domcontentloaded'});
      if (response?.status() !== 200) throw new Error('Anonymous GitHub page unavailable');
      const article = page.locator('article.markdown-body').first();
      await article.waitFor();
      const images = article.locator('img');
      if (await images.count() !== 9) throw new Error('Unexpected public README image count');
      for (const image of await images.all()) {
        await image.scrollIntoViewIfNeeded();
        await image.evaluate(element => element.decode());
        if (!await image.evaluate(element => element.naturalWidth > 0)) throw new Error('Broken public image');
      }
      await article.locator('h1').first().scrollIntoViewIfNeeded();
      await page.screenshot({path:`artifacts/github-public/${name}-${width}-top.png`});
      await images.nth(3).screenshot({path:`artifacts/github-public/${name}-${width}-panel.png`});
      console.log(`${name} ${width}px: anonymous GitHub 200, nine README images loaded`);
      await page.close();
    }
  }
} finally { await browser.close(); }
