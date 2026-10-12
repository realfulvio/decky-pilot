# Test plan and evidence

## Current situation-aware extension

This section supersedes historical counts below. Local Windows checks: **182 backend passed, two Linux-only process checks skipped; 27 frontend; 13 tooling; six browser tests**. Lint, TypeScript, Ruff and build pass. JavaScript audit and OSV audit of five shipped Python pins report zero advisories. Commands: `corepack pnpm verify`, `.venv/Scripts/python.exe -m ruff check backend main.py scripts tests/backend`, `.venv/Scripts/python.exe -m pytest -q --basetemp artifacts/pytest-context`, `corepack pnpm exec playwright test`, `node scripts/audit.mjs`, `.venv/Scripts/python.exe scripts/audit_python.py`. Stop the Vite preview before backend tests: its watcher can interfere with atomic temporary-file replacement on Windows.

Coverage adds official ChatGPT state/nonce/client/JWKS/identity/expiry/grant checks, renewal/revocation and terminal SSE/plan limits; six service-returned catalogs and bounded pagination; real xAI protocol fixtures/image modalities; game switch, revoked consent, 45-second image freshness, ambiguity, retained clarification replies, >=90-second admission and menu/loading abstention. A real local HTTP callback exercises the temporary loopback server with a **simulated identity service**; generated RSA keys exercise real JWT signing/verification. No real account authorization or paid inference was run.

Fifteen actual browser views plus fifteen panel captures use synthetic data, fake replies and explicitly simulated capture availability. `source.json` gives the committed capture source. GitHub-rendered EN/IT README/gallery and actual anonymous public pages must be checked after final publication. Source/history scans and PNG metadata review are repeated for new commits. Final CI runs, artifact links and published heads are in WORK_CHECKPOINT; earlier run links below certify only their listed revisions.

Linux CI runs the two platform-specific checks and verifies the extracted CPython 3.11 Pillow/PyJWT/cryptography runtime, using SHA-pinned Linux wheels. **Steam Deck and live-provider acceptance remain NOT RUN.** Safe atomic game-only capture is still blocked; manual import does not complete it.

## Resumed delivery, 13 October 2026

Current local verification: **146 Python passed, no skips; 22 frontend; 13 tooling; six browser tests**. Both symlink cases execute on this workstation now. Frozen install, ESLint/TypeScript/Ruff, zero-advisory audit, secret scan, build, pinned vendor and package verification pass. Installable archive: 224 allowlisted files. Final source/package ZIPs must be regenerated after the delivery commit; current Linux CI also runs the isolated extracted-package runtime smoke.

Added regressions cover OpenAI incomplete/max_output_tokens text and usage retention without increased budget/retries, rejection of other incomplete/failed states and empty reasoning-only output, context revision/session/removal, detected Steam game in Game/onboarding, and draft preservation during unchanged polling/settings updates. Regressions failed before fixes.

Presentation: twenty actual browser screenshots (ten full views plus ten direct panel captures) from committed source `d192330cc36816c7e15d522932de0c1202c240d1`; synthetic fixtures, no device/API/audio. Both README languages and gallery use GitHub Markdown API output for visual QA at 1200/390 pixels, all images decode, 39 relative links resolve, and no page overflow occurs. The single-column gallery keeps phone text readable. Concept cover and editable workflow diagrams are distinctly labelled. Original brand PNG bytes remain intact.

Public-history audit: all reachable blobs/commits and historical raster images, with author/path/source/PR review. No credential/private image finding remains; an exact `user:pass@localhost` SSRF rejection fixture is documented as synthetic. Repeat history scan after final commits. WORK_CHECKPOINT records final CI/publication evidence. Main contains only the presentation, while both PRs remain open and unmerged.

Actual Linux delivery runs [MVP 38315477004](https://github.com/realfulvio/decky-pilot/actions/runs/38315477004), [push 38315471465](https://github.com/realfulvio/decky-pilot/actions/runs/38315471465) and [gallery 38315386247](https://github.com/realfulvio/decky-pilot/actions/runs/38315386247) passed with 146 backend/22 frontend/13 tooling/six browser tests, no skips, clean audit and successful extracted ZIP/native Pillow lifecycle. The repository was then made PUBLIC as explicitly authorized. Actual anonymous GitHub README rendering verifies all nine images in each language at 1200/390 pixels. Subsequent final documentation/relative-image URL commits must also have green current checks.

Final relative-image/diagram fixes and publication evidence passed [MVP PR 38315934418](https://github.com/realfulvio/decky-pilot/actions/runs/38315934418), [push 38315928211](https://github.com/realfulvio/decky-pilot/actions/runs/38315928211) and [gallery 38315935922](https://github.com/realfulvio/decky-pilot/actions/runs/38315935922). Actual public main is presentation-only; no merge commits exist. WORK_CHECKPOINT and the PRs' current checks track the final evidence-only documentation follow-up.

Review date: 12 October 2026. Local workstation: Windows, Node 24.20.0, pnpm 10.28.2, Python 3.13.15, Microsoft Edge browser. CI: Ubuntu 24.04, Node 24.20.0, Python 3.11.7, Chromium. Steam Deck: **NOT RUN**.

| Check | Latest local evidence | Coverage |
|---|---|---|
| Frozen install | PASS | Lockfile exact resolutions/integrity |
| ESLint / TypeScript | PASS | Production components/strict types |
| Frontend Vitest | PASS, 16 tests | Three-step onboarding, cleared keys, complete catalogs, independent languages, no diagnostics, errors, image approval, pending/cancel; contracts/popup/Steam/listeners/audio cleanup |
| Tooling node tests | PASS, 13 tests | Confined cleanup/symlink refusal, audit high/critical/former exemption/registry failure |
| Ruff | PASS | Backend/lifecycle/scripts/tests |
| Python pytest | PASS, 132 passed / 2 skipped | Four native protocols, storage/session/scheduler/network/privacy/images/TTS, localization, disabled real capture adapter and synthetic capture lifecycle/session consent |
| Playwright | PASS, 6 tests | English at 1280x800/720, focus/scroll/no overflow/errors, Italian independent defaults, per-image approval; narrow 360x800/720 and menu 20/24/32px |
| Secret scan | PASS | No detected key/PEM matches; values never printed |
| Registry audit + policy | PASS, zero advisories | No exception; high/critical and unavailable audit fail |
| Rollup build | PASS | Official WASM, external React/Decky, no harness runtime |
| Vendor / ZIP verify | PASS | Pinned Linux CP311 Pillow wheel, catalogs, licenses, layout/allowlist/checksum |

Local Windows skips are the two symlink cases because privileges are unavailable. Linux CI executes them and POSIX permission assertions without skips. Before the redesign, [PR run 38306051080](https://github.com/realfulvio/decky-pilot/actions/runs/38306051080) passed the complete workflow, including 118 Python tests and isolated extracted ZIP smoke. The redesign commit `24062b35792db808131b4d68fdf4e0ed6233214f` passed [PR run 38309142059](https://github.com/realfulvio/decky-pilot/actions/runs/38309142059): **130 Python tests, no skips; 15 frontend; 13 tooling; four browsers; zero audit advisories; build/vendor/package and isolated extracted ZIP runtime all passed**. The workflow artifact was uploaded successfully. Final delivery checks are also attached to PR #1.

The extracted-package smoke runs `python -I` outside the checkout, asserts that Pillow and its native `_imaging` load from the ZIP, encodes/decodes PNG and starts/status-checks/unloads the packaged backend with only the Decky lifecycle shim. This validates Linux CP311 packaging, not an actual Loader installation or Deck ABI.

## Test isolation

Backend fixtures block DNS and the production transport entry point. Native adapter tests inject HTTP/process responses, inspect actual request payloads/auth/vision/output/usage and test 401/403/404/429/5xx, timeout and malformed/empty/blocked replies. Network-worker tests inject DNS/socket/HTTP and check pinned IP/size/redirect behavior. Synthetic credentials/images never leave the test process. Windows asyncio loopback wakeups are not provider calls.

Capture tests use explicit synthetic subprocesses/test-only injection, check fixed CLI arguments/focus refusal/private cleanup, approval, immediate guard cancellation, current-session consent and 89/90-second behavior. Production capture remains disabled in a separate assertion. No screenshot acquisition on SteamOS is certified by these tests.

Shared JSON Schema fixtures and actual backend records/events are validated in Python and TypeScript. Catalog key/placeholders parity and English/Italian safe errors are checked. Browser tests run the same App with labelled DOM stand-ins; production uses Decky controls. Keyboard focus tests are not controller tests.

## Deferred checks

[Hardware checklist](HARDWARE_VALIDATION.md): actual SteamOS/Decky/Python ABI/UID, install/load, controller/keyboard, Steam detection, picker, QAM toast, TTS routing/IPC and CPU/RAM/frame-rate/sleep-resume measurements. [Capture safety criteria](CAPTURE_VERIFICATION.md) require a safe acquisition mechanism before a hardware enablement test. Optional live provider smoke requires separate explicit permission/credentials and has not been run.

Branding revision additionally verifies explicit language/consent/key/history preservation, assistant-language speech independent of UI/legacy voice field, official-docs cloud image admission and no silent model substitution. Original raster branding is preserved; the hand-drawn menu SVG was visually inspected at 20/24/32 pixels in the browser. Production Decky controller and actual API account access remain deferred.

## Final branding implementation evidence

Commit `c27050bef0c4b59a0019e382b166669d251b4059` passed [PR Linux run 38311241604](https://github.com/realfulvio/decky-pilot/actions/runs/38311241604) and its push workflow: **134 Python tests with no skips, 16 frontend, 13 tooling and six browser tests**. Lint/types/Ruff/secret scan, zero-advisory audit, build/vendor/package and isolated extracted ZIP runtime all passed. The uploaded artifact contains install/source ZIPs and checksums; the installable archive has 194 allowlisted files. Current PR checks must also pass after documentation/gallery updates.

Original logo/icon bytes were compared with `1b5cc03` and match exactly. Ten English offline gallery screenshots were visually reviewed (Play/Game/welcome/guided setup/service-sharing/languages/image approval/pending/720-pixel answer/voice), with explicit synthetic and unavailable-capture states. Regeneration records its committed source revision alongside the images.
