// Adapted from @decky/rollup 1.0.2 (BSD-3-Clause; attribution in LICENSE).
// Keep Decky's runtime globals without the vulnerable glob-based delete chain.
import { readFileSync } from 'node:fs';
import commonjs from '@rollup/plugin-commonjs';
import json from '@rollup/plugin-json';
import { nodeResolve } from '@rollup/plugin-node-resolve';
import replace from '@rollup/plugin-replace';
import typescript from '@rollup/plugin-typescript';
import externalGlobals from 'rollup-plugin-external-globals';
import importAssets from 'rollup-plugin-import-assets';
import { cleanDist } from './scripts/clean_dist.mjs';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('.', import.meta.url));
const manifest = JSON.parse(readFileSync(new URL('./plugin.json', import.meta.url), 'utf8'));

export default {
  input: './src/index.tsx',
  plugins: [
    { name: 'deckpilot-clean-dist', buildStart() { cleanDist(root); } },
    typescript(), json(), commonjs(), nodeResolve({ browser: true }),
    externalGlobals({
      react: 'SP_REACT', 'react/jsx-runtime': 'SP_JSX', 'react-dom': 'SP_REACTDOM',
      '@decky/ui': 'DFL', '@decky/manifest': JSON.stringify(manifest),
    }),
    replace({ preventAssignment: false, 'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV || 'production') }),
    importAssets({ publicPath: `http://127.0.0.1:1337/plugins/${manifest.name}/` }),
  ],
  context: 'window',
  external: ['react', 'react-dom', '@decky/ui'],
  treeshake: { pureExternalImports: { pure: ['@decky/ui', '@decky/api'] }, preset: 'smallest' },
  output: {
    dir: 'dist', format: 'esm', sourcemap: true, exports: 'default',
    sourcemapPathTransform: path => path.replace(/^\.\.\//, `decky://decky/plugin/${encodeURIComponent(manifest.name)}/`),
  },
};
