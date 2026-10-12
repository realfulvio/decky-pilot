# Backlog

Closed means implemented and verified offline/CI, not hardware certified. IDs are local tracking references; no matching GitHub issues are claimed.

| ID | Priority / work | Status / acceptance |
|---|---|---|
| DP-001 | P0 bootstrap / official APIs | Closed: pinned sources/build/CI; API_VERIFICATION |
| DP-002 | P0 RPC/shared contract | Closed: allowlists/ranges/safe errors, Python and TypeScript schema tests |
| DP-003 | P0 settings/secrets | Closed: atomic writes/migration/delete, Linux POSIX and symlink tests; Deck UID pending |
| DP-004 | P0 OpenAI Responses/vision | Closed offline: real native requests, auth/store:false/output/usage/error fixtures |
| DP-005 | P0 Gemini | Closed offline: native parts/inlineData/key header, thought filtering/errors |
| DP-006 | P0 Claude | Closed offline: Messages/system/version/images; single-workspace key limitation documented |
| DP-007 | P0 Ollama/network | Closed offline: authorized endpoint, model capability check, DNS/SSRF/redirect controls |
| DP-008 | P0 context/session/Steam adapter | Closed offline: manual no-AppID, stale rejection, unknown/ambiguous fallback; actual Steam pending |
| DP-009 | P0 scheduler | Closed offline: >=90s, no resume burst, fresh context, session consent, pause/dedup/error/budget |
| DP-010 | P0 popup/full conversation | Closed offline: six seconds/no sound/dismiss/full reply; QAM visibility pending |
| DP-011 | P0 manual visual assistance | Closed offline: actual image decode/clean/preview, one-use destination approval, multimodal fixtures; Deck picker pending |
| DP-012 | P0 voice/Stop | Closed offline: existing espeak-ng/OpenAI Speech, independent pronunciation, cleanup/fallback; routing pending |
| DP-013 | P0 tests/CI/package | Closed: Linux tests and isolated extracted-package smoke; TEST_PLAN |
| DP-014 | P0 privacy/security | Closed: conservative defaults/consents/deletion/retention; vulnerable build chain removed, no audit exception |
| DP-015 | P1 device compatibility | Open: ABI/UID/install/real Decky controller/picker/popup/audio/IPC, HARDWARE_VALIDATION |
| DP-016 | P1 Gaming Mode acquisition / automatic visual help | Open: real adapter and session flow implemented, production disabled; atomic safe game targeting and hardware evidence required, CAPTURE_VERIFICATION |
| DP-017 | P1 performance/resume | Open: actual CPU/RAM/latency/frame rate/wakeup measurements |
| DP-018 | P2 streaming | Open: native parsers/backpressure/cancel/tests; no fake tokens |
| DP-019 | P2 controller shortcut | Open: verified mapping/explicit toggle/no stolen game input |
| DP-020 | P2 STT/OCR/retrieval/profiles | Open: separately scoped permissions/limits/sources/tests |
| DP-021 | P0 international UI | Closed offline: shared complete en/it catalogs, three independent language settings, guided simple Decky UI; hardware navigation pending |
| DP-022 | P0 review gallery | Existing PR #2 coordinated with PR #1, English offline images; never presented as actual Deck capture |

Remote: `https://github.com/realfulvio/deckpilot.git`. MVP branch `codex/deckpilot-mvp`, [PR #1](https://github.com/realfulvio/deckpilot/pull/1). Gallery branch `docs/ui-gallery`, [PR #2](https://github.com/realfulvio/deckpilot/pull/2), based on the MVP. Neither is merged.
