// Report every advisory; reject every high/critical and unavailable audit. No exceptions.
import { spawnSync } from 'node:child_process';
import { dirname, join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

export function checkAudit(run, report = console.log) {
  if (run.error || run.signal || ![0, 1].includes(run.status)) throw new Error('Audit unavailable; no silent pass');
  let audit;
  try { audit = JSON.parse(run.stdout); } catch { throw new Error('Audit unavailable; invalid JSON'); }
  const counts = audit?.metadata?.vulnerabilities;
  if (audit?.error || !audit?.advisories || !counts ||
      !['info', 'low', 'moderate', 'high', 'critical'].every(key => Number.isInteger(counts[key]) && counts[key] >= 0)) {
    throw new Error('Registry audit failed or incomplete');
  }
  const advisories = Object.values(audit.advisories);
  let failed = counts.high > 0 || counts.critical > 0;
  for (const advisory of advisories) {
    if (!['info', 'low', 'moderate', 'high', 'critical'].includes(advisory.severity)) throw new Error('Unknown audit severity');
    report(`${advisory.severity}: ${advisory.github_advisory_id} (${advisory.module_name})`);
    failed ||= ['high', 'critical'].includes(advisory.severity);
  }
  if (!advisories.length && Object.values(counts).some(count => count > 0)) throw new Error('Incomplete advisory report');
  if (!advisories.length) report('Dependency audit: no advisories');
  return failed ? 1 : 0;
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  const windows = process.platform === 'win32';
  const command = windows ? process.execPath : 'corepack';
  const args = [...(windows ? [join(dirname(process.execPath), 'node_modules/corepack/dist/corepack.js')] : []), 'pnpm', 'audit', '--json'];
  process.exitCode = checkAudit(spawnSync(command, args, { encoding: 'utf8', timeout: 60000 }));
}
