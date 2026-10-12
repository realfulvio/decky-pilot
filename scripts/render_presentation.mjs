// Render GitHub's actual Markdown API output for local visual QA.
// Public presentation text only; credentials are handled by gh and never logged.
import {chromium} from '@playwright/test';
import {execFileSync} from 'node:child_process';
import {readFile, mkdir} from 'node:fs/promises';
import {resolve, join, extname} from 'node:path';
const root = resolve(process.argv[2] ?? '.');
const output = resolve('artifacts/github-preview');
await mkdir(output, {recursive:true});
const browser = await chromium.launch({channel: process.env.PLAYWRIGHT_CHANNEL === 'chromium' ? undefined : 'msedge'});
try {
  for (const name of ['README.md', 'README.it.md', 'docs/UI_GALLERY.md']) {
    const text = await readFile(join(root, name), 'utf8');
    let html = execFileSync('gh', ['api', 'markdown', '--input', '-'], {
      input: JSON.stringify({text, mode:'gfm', context:'realfulvio/decky-pilot'}), encoding:'utf8'
    });
    const base = resolve(root, name, '..');
    for (const match of [...html.matchAll(/src="([^"]+)"/g)]) {
      const src = match[1];
      if (/^https?:/.test(src)) throw new Error(`Unexpected remote image in ${name}`);
      const path = resolve(base, src.split(/[?#]/, 1)[0]);
      if (!path.startsWith(root)) throw new Error('Image escaped presentation root');
      const bytes = await readFile(path);
      const mime = extname(path) === '.svg' ? 'image/svg+xml' : 'image/png';
      html = html.replace(match[0], `src="data:${mime};base64,${bytes.toString('base64')}"`);
    }
    for (const width of [1200, 390]) {
      const page = await browser.newPage({viewport:{width,height:900}});
      await page.setContent(`<meta charset="utf-8"><style>
        *{box-sizing:border-box}body{margin:0;padding:24px;color:#1f2328;background:#fff;font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}
        .markdown-body{max-width:980px;margin:auto;overflow-wrap:break-word}.markdown-body img{max-width:100%;height:auto}
        h1,h2{padding-bottom:.3em;border-bottom:1px solid #d1d9e0;line-height:1.25}h1{font-size:32px}h2{font-size:24px;margin-top:32px}
        a{color:#0969da;text-decoration:none}a:hover{text-decoration:underline}p{margin:0 0 16px}blockquote{margin:0 0 16px;padding:0 16px;color:#59636e;border-left:4px solid #d1d9e0}
        table{border-collapse:collapse;display:block;width:max-content;max-width:100%;overflow:auto;margin-bottom:16px}td,th{border:1px solid #d1d9e0;padding:8px 13px}tr:nth-child(2n){background:#f6f8fa}
        pre{padding:16px;overflow:auto;border-radius:6px;background:#f6f8fa;font-size:13px}code{font-family:ui-monospace,Consolas,monospace}p code,li code{background:#eff1f3;padding:.2em .4em;border-radius:6px}
        .anchor{display:none}li{margin:4px 0}@media(max-width:500px){body{padding:16px}h1{font-size:28px}}
        </style><article class="markdown-body">${html}</article>`);
      await page.evaluate(async () => { await Promise.all([...document.images].map(image => image.decode())); });
      const broken = await page.evaluate(() => [...document.images].some(image => !image.naturalWidth));
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth);
      if (broken || overflow) throw new Error(`Broken image/page overflow: ${name} at ${width}`);
      const label = name.replaceAll('/', '-').replace('.md', '');
      await page.screenshot({path:join(output,`${label}-${width}-full.png`),fullPage:true});
      await page.screenshot({path:join(output,`${label}-${width}-top.png`)});
      if (name.startsWith('README')) {
        await page.locator('img').nth(2).screenshot({path:join(output,`${label}-${width}-workflow.png`)});
        await page.locator('table').first().screenshot({path:join(output,`${label}-${width}-status.png`)});
        await page.locator('img').nth(3).screenshot({path:join(output,`${label}-${width}-gallery.png`)});
      }
      console.log(`${name} ${width}px: GitHub-rendered HTML, all images decoded, no page overflow`);
      await page.close();
    }
  }
} finally { await browser.close(); }
