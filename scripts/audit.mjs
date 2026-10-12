// Fail new high/critical advisories. One scoped, unpatched build-only exception is documented.
import { spawnSync } from 'node:child_process';
import { dirname, join } from 'node:path';
const windows = process.platform === 'win32';
const command = windows ? process.execPath : 'corepack';
const args = [...(windows ? [join(dirname(process.execPath), 'node_modules/corepack/dist/corepack.js')] : []), 'pnpm', 'audit', '--json'];
const run = spawnSync(command, args, {encoding: 'utf8'});
let audit;
try { audit = JSON.parse(run.stdout); } catch { throw new Error('Audit unavailable; no silent pass'); }
const advisories = Object.values(audit.advisories ?? {});
for (const advisory of advisories) {
  const permitted = advisory.github_advisory_id === 'GHSA-vfj7-8cjw-p6xm' && advisory.module_name === 'braces' &&
    advisory.findings.every(f => f.paths.every(p => p.includes('@decky/rollup>rollup-plugin-delete>')));
  console.log(`${advisory.severity}: ${advisory.github_advisory_id} (${advisory.module_name})${permitted ? ' · scoped build-only exception; see docs/SECURITY.md' : ''}`);
  if (['high', 'critical'].includes(advisory.severity) && !permitted) process.exitCode = 1;
}
if (audit.error) throw new Error('Registry audit failed');
if (!advisories.length) console.log('Dependency audit: no advisories');
