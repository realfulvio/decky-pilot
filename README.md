# Decky Pilot

> **Your AI copilot for Steam Deck. Get help tailored to your game, your screen, and the moment you’re playing.**

**Our product goal.** The MVP is in review. On 17 October 2026, installation, storage and the backend were first checked on an actual Steam Deck. Situation-aware help, account connections, the on-screen panel and automatic gameplay capture are not yet validated there. This page describes what is implemented, what has been tested, and what remains.

<p align="center"><img src="assets/brand/decky-pilot-logo-dark.png?raw=true" alt="Decky Pilot logo" width="320"></p>

[Italiano](README.it.md) · [UI gallery](docs/UI_GALLERY.md) · [MVP PR #1](https://github.com/realfulvio/decky-pilot/pull/1) · [Gallery PR #2](https://github.com/realfulvio/decky-pilot/pull/2)

![Concept artwork of Decky Pilot connecting a fictional handheld puzzle to screen analysis, clarification and optional voice](assets/presentation/cover-v2.png?raw=true)

*AI-generated concept illustration. It is not a device photograph, application screenshot or Steam Deck test.*

> **Public presentation, MVP in PRs.** `main` contains README, images and presentation documentation. Application code remains in the open PRs. No merge, release or Decky store publication has occurred. Automatic capture is currently disabled; manual import is its alternative, not its completion.

## How it works

![Concept workflow showing game confirmation, Help me now, separate capture and sharing consent, recent context and useful help](assets/presentation/how-it-works-v2-en.svg?raw=true)

1. **Identify your game.** Use the active Steam title when available, then confirm or correct it. Add a title manually for non-Steam games or uncertain detection.
2. **Press Help me now.** Include what you want to achieve or what you already tried.
3. **Choose what to share.** Capture permission and permission to send the image to your selected AI are separate. The current review build uses a manually imported PNG/JPEG, a cleaned preview and per-image approval. Automatic gameplay capture still needs a safe game-only integration and device validation.
4. **Get help for this moment.** The assistant combines a recent image, game title and session conversation. It separates visible observations from deductions, offers concrete steps, or asks one short clarification. Your reply becomes session context.
5. **Listen if you want.** Read the answer or use optional voice. Full solutions are the default spoiler preference; popup duration defaults to six seconds.

The diagram illustrates the intended end-to-end flow. Images do not reveal hidden quests, inventory or progress. Automatic suggestions require useful recent context, stay at least 90 seconds apart, avoid duplicate images/advice and overlapping requests, and abstain for recognized menus, loading or uncertain scenes. The session indicator and Pause control are implemented, but the production capture gate stays closed.

## What works today

**Status meanings:** “Available” means verified in the offline browser/backend review path on the MVP branch, not a released or device-certified plugin. “Verified on device (backend)” means checked on an actual Steam Deck without the on-screen panel. “Implemented — awaiting Steam Deck validation” means code and simulated protocol tests exist, but device acceptance is still NOT RUN. “Planned” means work remains beyond the existing implementation.

| Feature | Status | Evidence and practical limit |
|---|---|---|
| English-first UI, complete Italian, separate assistant/voice language | Available | Actual React browser rendering, localization tests and layout checks. |
| Manual game title, objective and session conversation | Available | Non-Steam/unknown titles, correction and session reset tested. |
| Manual image import, cleaned preview, named recipient approval | Available | PNG/JPEG validation, metadata removal, one-use image and 45-second send freshness tested. Device picker still needs validation. |
| Install, upgrade, uninstall, private storage and safe errors on Steam Deck | Verified on device (backend) | Decky Loader 3.2.10 and its CPython 3.11, `deck` user, 0700/0600 files, no keys in logs, idle CPU 0%. On-screen panel, controller and audio still pending. [Device evidence →](docs/HARDWARE_VALIDATION.md) |
| Active Steam game detection and game-switch handling | Implemented — awaiting Steam Deck validation | Guarded Steam/Decky information only; unknown/ambiguous detection suspends automation. Controller/device checks pending. |
| Contextual image estimates, concrete steps and one clarification | Implemented — awaiting Steam Deck validation | Structured visual replies validated; observations/deductions separated; session answers retained. Live-model quality not evaluated. |
| ChatGPT OAuth, developer APIs, catalogs and image gates | Implemented — awaiting Steam Deck validation | Native integrations and offline authentication/protocol tests. Real-account authorization and inference NOT RUN. |
| Capture adapter, session consent, automatic scheduling and immediate pause | Implemented — awaiting Steam Deck validation | Gamescope command adapter and simulated capture/scheduler tests; production acquisition disabled. |
| Safe atomic game-only acquisition and automatic capture enabled during play | Planned | Existing focus checks cannot prevent sensitive-screen acquisition during a transition. This is a central delivery blocker, not solved by manual import. |
| Six-second popup and optional local/online voice | Implemented — awaiting Steam Deck validation | Text fallback, consent and cancellation tested; actual QAM/controller/audio routing pending. |
| Consumer-account logins for Claude, Gemini or Grok | Planned | No compatible third-party consumer-plan flow has been established; no invented login is offered. |

## Fair play and your Steam account

Decky Pilot is not a cheat. It never reads or changes game memory or files, never injects code into a game, never sends controller or keyboard input, and never automates Steam. It runs as a separate Decky process and talks only to the AI service you choose. Even so, Steam's Subscriber Agreement and many games forbid outside help that gives an unfair advantage in multiplayer. Use Decky Pilot for single-player or non-competitive play, and follow each game's rules. [Account safety assessment →](docs/ACCOUNT_SAFETY.md)

## Choose your AI

All integrations below are implemented in the MVP PR, with simulated service tests. **No live account, paid API inference or Steam Deck provider test has been performed.** Model names come from the selected service; no GPT-5.6/GPT-6.1 entitlement is promised. Availability and image capability are separate checks.

| Provider / connection | Connection and usage | Image requirements |
|---|---|---|
| **ChatGPT plan** | Official local/open-source **Continue with ChatGPT** OAuth. Eligible account/workspace and explicit plan grant required. Backend renewal/disconnect; account-specific catalog. Subject to ChatGPT app limits and settings. | Returned account model plus independently verified image support. Unknown models remain text-only. |
| **OpenAI API — advanced** | Developer API key; `/v1/models` and Responses. **Separate API billing**, not ChatGPT subscription access. | Actual catalog selection and reviewed exact image-capable model ID. |
| **Claude** | Claude Console API key, Models and Messages APIs. Developer API billing/limits; use a single-workspace key. No consumer-plan login. | Reviewed exact image-capable model; unknown IDs are text-only. |
| **Gemini** | AI Studio API key and project quotas/billing. Google consumer subscriptions do not establish API access. | Returned generateContent model plus reviewed image support. |
| **Grok** | Official xAI API key, language-model catalog and Responses. API account/credits and separate API terms; no consumer subscription assumption. | Returned `input_modalities` must include `image`. No image-generation-model substitution. |
| **Ollama** | Explicitly approved local/LAN endpoint and installed model. No API key required for the supported local route; a server may itself forward to cloud. | `/api/show` must report `vision` before sending an image. |

Catalog requests are explicit and send no game text/image; ChatGPT sign-in also retrieves its account catalog. Partial catalogs are labelled. No model/provider or paid fallback happens after errors. [Official sources, implementation details and exact verification gaps →](docs/PROVIDER_VERIFICATION.md)

## A look at the interface

**Real browser screenshots of the React App with labelled HTML stand-ins and synthetic data.** These show implemented UI, not Steam Deck captures, live AI results or working hardware capture. Production injects Decky controls; controller acceptance remains pending.

### Welcome and onboarding

<img src="docs/images/ui/panel-03-onboarding.png?raw=true" alt="Actual browser screenshot of the first-use welcome" width="420">

### Choose an AI connection

<img src="docs/images/ui/panel-11-ai-connection.png?raw=true" alt="Actual browser screenshot of AI selection and ChatGPT account setup with no connected account" width="420">

### Separate capture consent

<img src="docs/images/ui/panel-12-capture-consent.png?raw=true" alt="Actual browser screenshot of capture approval controls using simulated capture availability" width="420">

*Capture availability is simulated in this screenshot. It does not demonstrate acquisition on hardware.*

### Review before sending

<img src="docs/images/ui/panel-06-image-review.png?raw=true" alt="Actual browser screenshot of a synthetic image and separate permission to share it with the selected recipient" width="420">

### Help me now and contextual steps

<img src="docs/images/ui/panel-01-play.png?raw=true" alt="Actual browser screenshot of Help me now and synthetic contextual observations and next steps" width="420">

### Concrete next steps

<img src="docs/images/ui/panel-15-contextual-answer.png?raw=true" alt="Actual browser screenshot of synthetic visible observations, labelled deductions and concrete steps" width="420">

### One useful clarification

<img src="docs/images/ui/panel-13-clarification.png?raw=true" alt="Actual browser screenshot of a simulated ambiguous scene and one short clarification question" width="420">

### Independent languages and settings

<img src="docs/images/ui/panel-05-languages.png?raw=true" alt="Actual browser screenshot of UI and assistant language settings" width="420">

### Optional voice

<img src="docs/images/ui/panel-10-voice.png?raw=true" alt="Actual browser screenshot of local and separately authorized OpenAI voice settings" width="420">

*Voice controls are real UI; this preview does not play speech.* [All fifteen views and capture provenance →](docs/UI_GALLERY.md)

## Installation and developer preview

The MVP is on `codex/deckpilot-mvp`, **not `main`**. There is no store release or validated device installation. Review ZIPs and SHA256 files are [CI artifacts](https://github.com/realfulvio/decky-pilot/actions), not a production recommendation.

```sh
git clone --branch codex/deckpilot-mvp https://github.com/realfulvio/decky-pilot.git
cd decky-pilot
corepack pnpm install --frozen-lockfile
corepack pnpm preview
```

Use Node 24.20.0 and pnpm 10.28.2. The preview at `http://127.0.0.1:5173` uses synthetic replies; its sign-in/capture demonstrations make no real authorization, inference or device capture. React/TypeScript frontend and Python backend remain separate. [Build, packaging and manual review installation](https://github.com/realfulvio/decky-pilot/blob/codex/deckpilot-mvp/docs/DEVELOPMENT.md).

## Privacy, credentials and limits

No telemetry or Decky Pilot central server. Keys and OAuth tokens stay in the backend's own protected local files and are never returned in status. Files are plaintext with owner-only Unix permissions, not encrypted storage; software with the same access can read them. No browser cookies or credentials from other applications are read. Disconnect attempts remote session revocation; failure is reported and local tokens are cleared.

History stays in memory unless you opt in. Images are cleaned, single-use, never added to conversation history and limited to one pending copy. An image prepared more than 45 seconds ago cannot be sent as current context; manual import cannot verify when the original file was captured. Acquisition and provider sharing are distinct consents. Changing recipient/account or revoking consent cancels pending work. Local deletion cannot retract provider data already sent.

Automatic requests have a minimum 90-second interval, a 20-attempt session budget, backoff and pause after repeated errors. ChatGPT preview requires streaming and does not accept a server-side output-token budget; local limits cannot promise a hard billing cap. Review [ChatGPT app usage](https://chatgpt.com/settings/usage) and your API provider's quotas before use. Online Speech uses a separate OpenAI API key/consent and can incur separate costs; ChatGPT plan sign-in does not authorize Speech.

[Privacy](https://github.com/realfulvio/decky-pilot/blob/codex/deckpilot-mvp/docs/PRIVACY.md) · [Security](https://github.com/realfulvio/decky-pilot/blob/codex/deckpilot-mvp/docs/SECURITY.md)

## Verification and roadmap

Offline suites cover OAuth validation/refresh/revocation, service catalogs, xAI payloads, unsupported vision, revoked consent, obsolete images, game changes, ambiguous scenes, clarification context, duplicates and automatic timing. Browser checks cover layouts and keyboard focus. Linux CI builds/packages and tests the extracted cryptographic/Pillow runtime. These are **simulated-service and real local checks**, not live-provider or device certification.

Next: establish safe atomic game-only capture and prove refusal of Steam/QAM/sign-in/account screens; test real account eligibility/catalogs/limits and visual inference; then validate Steam Deck install/ABI, controller, non-Steam detection, transitions, sleep/resume, voice and performance. See the [hardware checklist](https://github.com/realfulvio/decky-pilot/blob/codex/deckpilot-mvp/docs/HARDWARE_VALIDATION.md), [capture blocker](https://github.com/realfulvio/decky-pilot/blob/codex/deckpilot-mvp/docs/CAPTURE_VERIFICATION.md) and [test evidence](https://github.com/realfulvio/decky-pilot/blob/codex/deckpilot-mvp/docs/TEST_PLAN.md).

[Image provenance](docs/PRESENTATION_ASSETS.md) · [Publication review](docs/PUBLICATION_REVIEW.md) · [BSD-3-Clause license](https://github.com/realfulvio/decky-pilot/blob/codex/deckpilot-mvp/LICENSE)
