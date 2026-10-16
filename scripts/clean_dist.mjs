import { lstatSync, rmSync } from 'node:fs';
import { dirname, resolve } from 'node:path';

export function cleanDist(projectRoot) {
  const root = resolve(projectRoot);
  const target = resolve(root, 'dist');
  if (dirname(target) !== root) throw new Error('Build output must stay inside the project');
  let info;
  try { info = lstatSync(target); } catch (error) {
    if (error.code === 'ENOENT') return;
    throw error;
  }
  if (info.isSymbolicLink() || !info.isDirectory()) throw new Error('Unsafe build output directory');
  rmSync(target, { recursive: true });
}
