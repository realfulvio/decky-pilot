// Reproducible offline UI review. Run `corepack pnpm preview` separately first.
// Uses the real App with declared DOM stand-ins, never a Steam Deck capture.
import {chromium} from '@playwright/test';
import {mkdir, writeFile} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {join} from 'node:path';
const root = fileURLToPath(new URL('../', import.meta.url));
const output = join(root, 'artifacts', 'gallery');
await mkdir(output, {recursive:true});
const browser = await chromium.launch({channel:process.env.PLAYWRIGHT_CHANNEL === 'chromium' ? undefined : 'msedge'});
try {
  const page = await browser.newPage({viewport:{width:1280,height:800}});
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  const load = () => page.goto('http://127.0.0.1:5173');
  const button = name => page.getByRole('button', {name,exact:true});
  const shot = async name => {
    await page.screenshot({path:join(output,name)});
    await page.locator('.dp').screenshot({path:join(output,`panel-${name}`)});
  };
  await load(); await button('Help me now').waitFor();
  await shot('01-play.png');
  await button('Game').click(); await shot('02-game.png');
  await button('Preview first-time setup').click(); await button('Play').click();
  await shot('03-onboarding.png');
  await button('Get started').click(); await shot('09-guided-game.png');
  await load(); await button('Settings').click();
  await page.getByLabel('Allow game context and messages to be sent to this AI service', {exact:true}).scrollIntoViewIfNeeded(); await shot('04-service-sharing.png');
  await load(); await button('Settings').click(); await shot('05-languages.png');
  await page.getByRole('combobox', {name:'Voice service',exact:true}).scrollIntoViewIfNeeded(); await shot('10-voice.png');
  await load();
  // Synthetic PNG fixture, contains no real gameplay, key or account details.
  const png = Buffer.from(await page.evaluate(() => {
    const canvas = document.createElement('canvas'); canvas.width=480; canvas.height=240;
    const draw=canvas.getContext('2d'); if (!draw) throw new Error('Canvas unavailable');
    draw.fillStyle='#173043'; draw.fillRect(0,0,480,240);
    draw.fillStyle='#31738e'; draw.fillRect(180,42,120,170);
    draw.strokeStyle='#a5e8d9'; draw.lineWidth=5; draw.strokeRect(180,42,120,170);
    draw.fillStyle='#eaf4f6'; draw.font='32px sans-serif'; draw.fillText('△ ○ ◇',191,131);
    draw.font='14px sans-serif'; draw.fillText('SYNTHETIC TEST IMAGE — NOT GAMEPLAY',76,26);
    return canvas.toDataURL('image/png').split(',')[1];
  }), 'base64');
  await page.getByLabel('Game image file').setInputFiles({name:'synthetic.png',mimeType:'image/png',buffer:png});
  await page.getByAltText('Image to be shared, with metadata removed').waitFor();
  await button('Allow this image to be shared').scrollIntoViewIfNeeded(); await shot('06-image-review.png');
  await load(); await button('Toggle request delay').click();
  await page.getByLabel('Ask a question').fill('Which symbol should I choose?');
  await button('Ask Decky Pilot').click(); await button('Cancel').waitFor();
  await button('Cancel').scrollIntoViewIfNeeded(); await shot('07-pending.png');
  await load(); await page.setViewportSize({width:1280,height:720});
  await button('Stop').scrollIntoViewIfNeeded(); await shot('08-play-720.png');
  await load(); await page.setViewportSize({width:1280,height:800});
  await button('Preview ChatGPT setup').click(); await button('Get started').click(); await button('Next').click();
  await page.getByLabel('AI service', {exact:true}).scrollIntoViewIfNeeded(); await shot('11-ai-connection.png');
  await button('Continue with ChatGPT').scrollIntoViewIfNeeded(); await shot('14-chatgpt-sign-in.png');
  await load(); await button('Preview capture controls (simulated)').click(); await button('Help me now').click();
  await button('Capture game image').scrollIntoViewIfNeeded(); await shot('12-capture-consent.png');
  await load(); await button('Preview clarification').click();
  await page.getByText('Which objective are you trying to complete?', {exact:false}).scrollIntoViewIfNeeded(); await shot('13-clarification.png');
  if (errors.length) throw new Error('Gallery encountered browser errors');
  const commit = execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim();
  await writeFile(join(output,'source.json'),JSON.stringify({commit,mode:'actual React browser harness; synthetic data, AI replies and capture availability; no sign-in, live inference, speech or device capture',images:28,fullViewportImages:14,panelImages:14,browser:process.env.PLAYWRIGHT_CHANNEL === 'chromium' ? 'Chromium' : 'Microsoft Edge',capturedAt:new Date().toISOString()},null,2)+'\n');
  process.stdout.write(`Saved fourteen English views and fourteen panel screenshots from ${commit} to ${output}\n`);
} finally { await browser.close(); }
