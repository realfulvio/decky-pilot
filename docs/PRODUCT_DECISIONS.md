# Current product decisions

This addendum records the owner's 12 October 2026 `DECKY_PILOT_NEXT_TASK.md`, read in full. It supersedes conflicting product choices in the preserved original `DECKPILOT_CODEX_SPEC.md` and earlier intermediate implementations. Do not rebuild the project or reinstate obsolete defaults.

- Public name: **Decky Pilot**. Repository: `realfulvio/decky-pilot`; origin `https://github.com/realfulvio/decky-pilot.git`. Workspace and branch remain `C:/Users/Admin/deckpilot` and `codex/deckpilot-mvp`.
- Continue existing PR #1 and coordinate gallery PR #2. The owner's subsequent 13 October instruction explicitly authorizes PUBLIC visibility after current file/history audit and verification, and presentation-only README/translations/images/docs on main. No application code on main, merge, new/replacement PR, release, store or device installation. WORK_CHECKPOINT tracks delivery.
- English-default interface, onboarding, safe errors, README/public docs/issues/gallery/PR text. Complete Italian catalogs and README translation; stable keys/interpolation/English fallback.
- Two user language controls: interface and assistant. The assistant response language governs both generated answers and synthesized speech. This replaces the earlier independent voice-language selector. The stored `ttsLanguage` field remains accepted/preserved for compatibility, but no longer overrides assistant speech. Explicit interface/response preferences, keys, history and valid consent records are retained. New fields default to English.
- Real Decky UI: compact identity/game/readiness, dominant Help me now, question, latest answer/Listen/Stop, immediate automatic pause and secondary history/Game/Settings. Provider/model/keys/consents and advanced details stay out of Play. Browser controls are declared stand-ins, not proof of controller behavior.
- Original logo/icon PNGs from commits `c60e6d7`/`1b5cc03` stay intact. The branding-only commit was cherry-picked without merging either PR. A separately hand-drawn matching SVG supplies a legible menu mark; it is not a relabelled or automatically vectorized PNG. Preserve Loader manifest name `DeckPilot`, package/RPC/storage identifiers and archive root so existing data remains reachable.
- Visual analysis uses official OpenAI/Claude/Gemini requests with documented image-input models in `contracts/vision-models.json`; Ollama additionally checks `/api/show`. Model/account access is still separate from public documentation support. Never silently substitute a model/provider or use website cookies/subscription credentials.
- Reliable game-only acquisition remains unestablished: Gamescope has a real screenshot command but no atomic game-window binding. Concrete adapter and session lifecycle are implemented with production capture disabled. Manual image import/preview/remove/recipient approval works. No claim to have seen a game screen without an actual approved image.
- Optional automatic acquisition AND sending needs separate current-session consent, visible state, immediate pause, >=90-second admission cooldown, useful fresh context, dedup/error controls and bounded attempts; currently unavailable with capture disabled. No account/key/settings/arbitrary desktop capture, continuous streaming or catch-up bursts.
- Visible observations and hypotheses are distinct in model policy; hidden missions/inventory/progress cannot be reconstructed from one image. No fabricated game state/web verification or tools/gameplay control.
- Preserve full-solutions spoiler default, six-second popup/full reply, voice preference subject to capability/separate remote consent, backend secrets/private storage/cleanup/retention, no telemetry or recipient fallback.

Offline tests, Linux CI and package checks are required now. Actual SteamOS installation, atomically safe acquisition, Decky/controller/focus, QAM popup, audio routing/IPC and performance remain **NOT RUN** until hardware is available. See CAPTURE_VERIFICATION, HARDWARE_VALIDATION and TEST_PLAN.
# Situation-aware extension (14 October 2026)

The latest authorized scope adds separate ChatGPT plan OAuth and OpenAI API-key connections,
native Grok/xAI, service-returned model catalogs, verified image gates and structured situation estimates.
No model name establishes availability or image support. Catalog access never authorizes gameplay
sharing. Consumer subscriptions do not authorize developer API calls. No paid/provider fallback.
Visual replies distinguish observations and deductions; ambiguous scenes yield one brief question,
retained with the player's reply in the session. Automatic output is structured, useful, non-repeated,
at least 90 seconds apart; menu/loading/unknown estimates abstain. Image send freshness is 45 seconds.
Automatic capture remains central and incomplete on hardware: the existing Gamescope CLI hook is
disabled until atomic game-only acquisition and sensitive-screen refusal are demonstrated.
Manual import remains an alternative. Read the newest WORK_CHECKPOINT and PROVIDER_VERIFICATION.

