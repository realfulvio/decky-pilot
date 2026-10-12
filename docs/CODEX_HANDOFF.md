# Codex handoff

Workspace: `C:/Users/Admin/deckpilot`. Existing branch: `codex/deckpilot-mvp`, base `main`. Remote **available and verified** (same repository ID 1416105266, renamed by the owner from `realfulvio/deckpilot`; old links redirect): `https://github.com/realfulvio/decky-pilot.git`.

- Existing MVP: [PR #1](https://github.com/realfulvio/decky-pilot/pull/1), head `codex/deckpilot-mvp`, base `main`.
- Existing gallery: [PR #2](https://github.com/realfulvio/decky-pilot/pull/2), head `docs/ui-gallery`, base `codex/deckpilot-mvp`. Update its English images/docs independently; do not merge it into the MVP to coordinate review.
- No new PR, merge, force push, reset, device installation, release/store or mini PC connection is authorized/performed. Preserve existing work and use normal commits/pushes.

The complete original `DECKPILOT_CODEX_SPEC.md` was read and preserved. Later user requirements supersede its Italian default and original layout: English default and complete Italian catalogs, independent interface/AI/voice language choices, guided simple UI, visual assistance and strict sensitive-screen exclusion. Historical bootstrap statements about a missing remote/PR are obsolete.

## Implemented

Real Decky components, Play/Game/Settings and three-step onboarding; primary Help me now, free question, actual image review, latest answer and voice. Provider/keys/permissions/languages/limits are Settings-only; diagnostics are not part of the user flow. Native OpenAI Responses, Claude Messages, Gemini generateContent and Ollama chat/show. Shared localized safe errors/policies, schema-compatible English defaults, independent voice pronunciation without translating answers. Sessions/cancel/idempotence, six-second popup/full history, cleaned one-use images, local/remote voice/Stop, private storage/deletion/retention.

Security commit `cefedad8497211990ea46a6a81991e2023886eba` removed the vulnerable Rollup preset/delete/glob/braces chain, preserved the bundle and removed the audit exemption. Zero advisories reported at review. CI now tests tooling and runs the actual extracted ZIP in isolated Linux CPython 3.11 outside the checkout, using vendored Pillow and Loader lifecycle. Verified successful [Linux run](https://github.com/realfulvio/decky-pilot/actions/runs/38306051080). Redesign commit `24062b35792db808131b4d68fdf4e0ed6233214f` also passed [Linux run 38309142059](https://github.com/realfulvio/decky-pilot/actions/runs/38309142059): 130 Python tests without skips, 15 frontend, 13 tooling, four browsers, clean audit and extracted-package smoke.

## Capture is deliberately unavailable

Official Valve sources establish `gamescopectl screenshot <path>`, base-plane-only output and asynchronous completion. A real bounded adapter is implemented/tested with synthetic subprocesses. The command lacks atomic game-window targeting; focus checks cannot guarantee no sensitive surface was acquired during transitions. `CAPTURE_SAFETY_VALIDATED=False`; no production screenshot or automatic visual acquisition is enabled. Manual images and native multimodal analysis remain implemented. Do not describe mocks/previews as working capture. CAPTURE_VERIFICATION records pinned source and acceptance criteria.

Per-session automatic consent, status/pause, >=90-second reservation, fresh useful context, dedup/error controls and 20-attempt budget are implemented/tested offline. Visual activation rejects unavailable capture. Consent is not restored after reload/game/settings/key changes. No continuous screenshot polling or inferred hidden progress.

## Verification and next work

TEST_PLAN separates local Windows checks, actual Ubuntu/Python 3.11 CI and hardware NOT RUN. Artifacts contain package/source ZIPs with adjacent SHA256 and English/Italian offline previews. The installable ZIP includes both catalogs and the full hash-pinned Linux CP311 Pillow wheel/licenses; source ZIP reflects HEAD and must be regenerated after the final commit.

Steam Deck unavailable. Next: review PR #1 and coordinated gallery #2; satisfy atomic capture safety criteria before enabling it; execute HARDWARE_VALIDATION on a future Deck and record ABI/UID/controller/picker/popup/audio/performance evidence. No real key or provider smoke is required for offline review. Do not recreate this project or request a device to complete verifiable work.

PR #2 already includes the owner's Decky Pilot raster branding assets/guidance. Preserve them while replacing the obsolete gallery. They remain separately reviewed assets; this MVP update does not claim their integration into the running plugin.
