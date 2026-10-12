# Third-party notices and licenses

DeckPilot is BSD-3-Clause (LICENSE). Configuration/lifecycle follow the Steam Deck Homebrew BSD template; its 2022-2024 copyright is preserved in LICENSE. No proprietary walkthrough or gameplay asset is distributed.

| Dependency | Use | License / distribution |
|---|---|---|
| @decky/api 1.1.3 | Bundled bridge | LGPL-2.1; full text docs/licenses/decky-api-LGPL-2.1.txt, corresponding source third_party/decky-api |
| @decky/ui 4.12.1 | External Loader runtime | LGPL-2.1; not redistributed in installable ZIP |
| Config adapted from @decky/rollup 1.0.2 | Build | BSD-3-Clause attribution in LICENSE; preset removed, direct plugin pins |
| tslib 2.8.1 | TypeScript helpers | 0BSD; full notice docs/licenses/tslib-0BSD.txt |
| React 19.1.1 | Harness; external in production | MIT; not bundled in installable ZIP |
| Pillow 12.3.0 | Decode/resize | HPND and native licenses in complete vendored wheel's dist-info/licenses/LICENSE |
| espeak-ng | Optional external process | GPL-3.0; no binary copied, installed or distributed |
| Test/build toolchain | Development | Not shipped as runtime; terms in installed dependencies |

Pillow transitive native licenses remain intact in the complete wheel. Original bundled-library notices are in docs/licenses. DeckPilot's BSD license does not replace Decky API/UI's LGPL. API 1.1.3 npm gitHead matches `d1b7f16070777a0ada939cbacd3606eeba0574f5`; corresponding unmodified source is included in `third_party/decky-api` and both generated archives.

The source archive contains committed frontend/backend/configuration/lockfile/API source. You may modify or replace the library and rebuild using README; no reverse-engineering restriction for debugging such modifications is imposed. To relink a variant, build `third_party/decky-api/src` using its included configuration, install the variant as a local dependency instead of @decky/api, and run `corepack pnpm build`. Other dependencies retain their terms.
