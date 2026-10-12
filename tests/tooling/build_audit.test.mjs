import assert from 'node:assert/strict';
import { test } from 'node:test';
import { mkdtempSync, mkdirSync, writeFileSync, existsSync, symlinkSync, rmSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { tmpdir } from 'node:os';
import { cleanDist } from '../../scripts/clean_dist.mjs';
import { checkAudit } from '../../scripts/audit.mjs';

function fixture(t) {
  const root = mkdtempSync(join(tmpdir(), 'deckpilot-build-'));
  t.after(() => {
    // Only remove the exact absolute directory created by this fixture.
    assert.equal(resolve(root), root);
    assert.equal(resolve(root, '..'), resolve(tmpdir()));
    rmSync(root, { recursive: true, force: true });
  });
  return root;
}

test('clean removes stale nested output while preserving project files', t => {
  const root = fixture(t);
  mkdirSync(join(root, 'dist', 'old'), { recursive: true });
  writeFileSync(join(root, 'dist', 'old', 'chunk.js'), 'stale');
  writeFileSync(join(root, 'keep.txt'), 'user data');
  cleanDist(root);
  assert.ok(!existsSync(join(root, 'dist')));
  assert.ok(existsSync(join(root, 'keep.txt')));
  cleanDist(root);
});

test('clean rejects a linked output and preserves its target', t => {
  const root = fixture(t);
  const outside = join(root, 'user-files');
  mkdirSync(outside);
  writeFileSync(join(outside, 'keep.txt'), 'user data');
  symlinkSync(outside, join(root, 'dist'), process.platform === 'win32' ? 'junction' : 'dir');
  assert.throws(() => cleanDist(root), /Unsafe/);
  assert.ok(existsSync(join(outside, 'keep.txt')));
});

test('clean rejects a file at the output path', t => {
  const root = fixture(t);
  writeFileSync(join(root, 'dist'), 'user data');
  assert.throws(() => cleanDist(root), /Unsafe/);
  assert.ok(existsSync(join(root, 'dist')));
});

function audit(severity) {
  const vulnerabilities = { info: 0, low: 0, moderate: 0, high: 0, critical: 0 };
  if (severity) vulnerabilities[severity] = 1;
  return { status: severity ? 1 : 0, stdout: JSON.stringify({
    advisories: severity ? { 1: { severity, github_advisory_id: 'GHSA-vfj7-8cjw-p6xm', module_name: 'braces' } } : {},
    metadata: { vulnerabilities },
  }) };
}

test('audit accepts a complete clean report', () => assert.equal(checkAudit(audit(), () => {}), 0));
for (const severity of ['high', 'critical', 'moderate']) {
  test(`audit reports ${severity}; high/critical always fail, including the former exception`, () => {
    const lines = [];
    assert.equal(checkAudit(audit(severity), line => lines.push(line)), severity === 'moderate' ? 0 : 1);
    assert.ok(lines[0].includes('GHSA-vfj7-8cjw-p6xm'));
  });
}
for (const run of [
  { status: 1, stdout: 'not JSON' }, { status: 0, stdout: '{}' },
  { ...audit(), status: null, error: new Error('network unavailable') },
  { ...audit(), status: 2 }, { ...audit(), signal: 'SIGTERM' },
  { status: 1, stdout: JSON.stringify({ error: 'registry unavailable' }) },
]) {
  test('audit rejects unavailable or incomplete reports', () => assert.throws(() => checkAudit(run, () => {})));
}
