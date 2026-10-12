# Test plan and evidence

Review date: 12 October 2026. Local workstation: Windows, Node 24.20.0, pnpm 10.28.2, Python 3.13.15, Microsoft Edge browser. CI: Ubuntu 24.04, Node 24.20.0, Python 3.11.7, Chromium. Steam Deck: **NOT RUN**.

| Check | Latest local evidence | Coverage |
|---|---|---|
| Frozen install | PASS | Lockfile exact resolutions/integrity |
| ESLint / TypeScript | PASS | Production components/strict types |
| Frontend Vitest | PASS, 15 tests | Three-step onboarding, cleared keys, complete catalogs, independent languages, no diagnostics, errors, image approval, pending/cancel; contracts/popup/Steam/listeners/audio cleanup |
| Tooling node tests | PASS, 13 tests | Confined cleanup/symlink refusal, audit high/critical/former exemption/registry failure |
| Ruff | PASS | Backend/lifecycle/scripts/tests |
| Python pytest | PASS, 128 passed / 2 skipped | Four native protocols, storage/session/scheduler/network/privacy/images/TTS, localization, disabled real capture adapter and synthetic capture lifecycle/session consent |
| Playwright | PASS, 4 tests | English at 1280x800/720, focus/scroll/no overflow/errors, Italian independent defaults, per-image approval |
| Secret scan | PASS | No detected key/PEM matches; values never printed |
| Registry audit + policy | PASS, zero advisories | No exception; high/critical and unavailable audit fail |
| Rollup build | PASS | Official WASM, external React/Decky, no harness runtime |
| Vendor / ZIP verify | PASS | Pinned Linux CP311 Pillow wheel, catalogs, licenses, layout/allowlist/checksum |

Local Windows skips are the two symlink cases because privileges are unavailable. Linux CI executes them and POSIX permission assertions without skips. Before the redesign, [PR run 38306051080](https://github.com/realfulvio/deckpilot/actions/runs/38306051080) passed the complete workflow, including 118 Python tests and isolated extracted ZIP smoke. Current redesign CI evidence is recorded below after observing the pushed revision; do not infer success from workflow configuration alone.

The extracted-package smoke runs `python -I` outside the checkout, asserts that Pillow and its native `_imaging` load from the ZIP, encodes/decodes PNG and starts/status-checks/unloads the packaged backend with only the Decky lifecycle shim. This validates Linux CP311 packaging, not an actual Loader installation or Deck ABI.

## Test isolation

Backend fixtures block DNS and the production transport entry point. Native adapter tests inject HTTP/process responses, inspect actual request payloads/auth/vision/output/usage and test 401/403/404/429/5xx, timeout and malformed/empty/blocked replies. Network-worker tests inject DNS/socket/HTTP and check pinned IP/size/redirect behavior. Synthetic credentials/images never leave the test process. Windows asyncio loopback wakeups are not provider calls.

Capture tests use explicit synthetic subprocesses/test-only injection, check fixed CLI arguments/focus refusal/private cleanup, approval, immediate guard cancellation, current-session consent and 89/90-second behavior. Production capture remains disabled in a separate assertion. No screenshot acquisition on SteamOS is certified by these tests.

Shared JSON Schema fixtures and actual backend records/events are validated in Python and TypeScript. Catalog key/placeholders parity and English/Italian safe errors are checked. Browser tests run the same App with labelled DOM stand-ins; production uses Decky controls. Keyboard focus tests are not controller tests.

## Deferred checks

[Hardware checklist](HARDWARE_VALIDATION.md): actual SteamOS/Decky/Python ABI/UID, install/load, controller/keyboard, Steam detection, picker, QAM toast, TTS routing/IPC and CPU/RAM/frame-rate/sleep-resume measurements. [Capture safety criteria](CAPTURE_VERIFICATION.md) require a safe acquisition mechanism before a hardware enablement test. Optional live provider smoke requires separate explicit permission/credentials and has not been run.
