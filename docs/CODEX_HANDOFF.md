# Codex handoff

Workspace: `C:/Users/Admin/deckpilot`. Existing branch: `codex/deckpilot-mvp`, base `main`. Remote **available and verified** (same repository ID 1416105266, renamed by the owner from `realfulvio/deckpilot`; old links redirect): `https://github.com/realfulvio/decky-pilot.git`.

- Existing MVP: [PR #1](https://github.com/realfulvio/decky-pilot/pull/1), head `codex/deckpilot-mvp`, base `main`.
- Existing gallery: [PR #2](https://github.com/realfulvio/decky-pilot/pull/2), head `docs/ui-gallery`, base `codex/deckpilot-mvp`. Update its English images/docs independently; do not merge it into the MVP to coordinate review.
- No new PR, merge, force push, reset, device installation, release/store or mini PC connection is authorized/performed. Preserve existing work and use normal commits/pushes.

The complete original `DECKPILOT_CODEX_SPEC.md` was read and preserved. Later user requirements supersede its Italian default and original layout: English default and complete Italian catalogs, independent UI/assistant language choices, with assistant language governing speech, guided simple UI, visual assistance and strict sensitive-screen exclusion. Historical bootstrap statements about a missing remote/PR are obsolete.

## Implemented

Real Decky components, Play/Game/Settings and three-step onboarding; primary Help me now, free question, actual image review, latest answer and voice. Provider/keys/permissions/languages/limits are Settings-only; diagnostics are not part of the user flow. Native OpenAI Responses, Claude Messages, Gemini generateContent and Ollama chat/show. Shared localized safe errors/policies, schema-compatible English defaults, assistant-language speech without translating old answers. Sessions/cancel/idempotence, six-second popup/full history, cleaned one-use images, local/remote voice/Stop, private storage/deletion/retention.

Security commit `cefedad8497211990ea46a6a81991e2023886eba` removed the vulnerable Rollup preset/delete/glob/braces chain, preserved the bundle and removed the audit exemption. Zero advisories reported at review. CI now tests tooling and runs the actual extracted ZIP in isolated Linux CPython 3.11 outside the checkout, using vendored Pillow and Loader lifecycle. Verified successful [Linux run](https://github.com/realfulvio/decky-pilot/actions/runs/38306051080). Redesign commit `24062b35792db808131b4d68fdf4e0ed6233214f` also passed [Linux run 38309142059](https://github.com/realfulvio/decky-pilot/actions/runs/38309142059): 130 Python tests without skips, 15 frontend, 13 tooling, four browsers, clean audit and extracted-package smoke.

## Capture is deliberately unavailable

Official Valve sources establish `gamescopectl screenshot <path>`, base-plane-only output and asynchronous completion. A real bounded adapter is implemented/tested with synthetic subprocesses. The command lacks atomic game-window targeting; focus checks cannot guarantee no sensitive surface was acquired during transitions. `CAPTURE_SAFETY_VALIDATED=False`; no production screenshot or automatic visual acquisition is enabled. Manual images and native multimodal analysis remain implemented. Do not describe mocks/previews as working capture. CAPTURE_VERIFICATION records pinned source and acceptance criteria.

Per-session automatic consent, status/pause, >=90-second reservation, fresh useful context, dedup/error controls and 20-attempt budget are implemented/tested offline. Visual activation rejects unavailable capture. Consent is not restored after reload/game/settings/key changes. No continuous screenshot polling or inferred hidden progress.

## Verification and next work

TEST_PLAN separates local Windows checks, actual Ubuntu/Python 3.11 CI and hardware NOT RUN. Artifacts contain package/source ZIPs with adjacent SHA256 and English/Italian offline previews. The installable ZIP includes both catalogs and the full hash-pinned Linux CP311 Pillow wheel/licenses; source ZIP reflects HEAD and must be regenerated after the final commit.

Steam Deck unavailable. Next: review PR #1 and coordinated gallery #2; satisfy atomic capture safety criteria before enabling it; execute HARDWARE_VALIDATION on a future Deck and record ABI/UID/controller/picker/popup/audio/performance evidence. No real key or provider smoke is required for offline review. Do not recreate this project or request a device to complete verifiable work.

PR #2 already includes the owner's Decky Pilot raster branding assets/guidance. Preserve them while replacing the obsolete gallery. The branding-only commit was cherry-picked into the MVP and integrated into README/onboarding/menu without merging either PR. Original opaque PNGs stay intact; a separate hand-drawn matching SVG is used for the small menu. Technical manifest/storage/RPC/archive names are preserved.

The latest owner task was read in full; PRODUCT_DECISIONS is the concise spec addendum. Response language now governs TTS; the earlier separate voice selector is superseded, but its stored field is preserved. Explicit language preferences, consent/secrets/history survive migration. The source-linked cloud vision catalog verifies image-input support publicly; access in the user account remains untested. Latest local branding checks: 132 Python passed/two Windows symlink skips, 16 frontend, 13 tooling, six browser tests including narrow 360-pixel layouts and 20/24/32-pixel menu inspection. Branding implementation commit `c27050bef0c4b59a0019e382b166669d251b4059` passed [Linux PR run 38311241604](https://github.com/realfulvio/decky-pilot/actions/runs/38311241604): 134 Python tests without skips, 16 frontend, 13 tooling, six browser tests, zero advisories, build/vendor/package and actual extracted ZIP runtime all passed. The artifact was uploaded successfully (194 installable files). Subsequent documentation/gallery commits must also have green current PR checks; consult GitHub rather than assuming historical checks cover a newer head.

Ten English gallery previews are regenerated from a committed MVP revision, with source metadata and explicit offline/synthetic labels. PR #2 intentionally replaces the eight obsolete captures, preserves their Git history and original branding, and stays based on the MVP. No PR has been merged.
