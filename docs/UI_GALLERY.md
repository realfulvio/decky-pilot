# Decky Pilot interface gallery

English previews of the implemented React application, captured on 13 October 2026 from MVP source commit `d192330cc36816c7e15d522932de0c1202c240d1`. Generated with `node scripts/capture_gallery.mjs`, Microsoft Edge, at 1280x800 (1280x720 for the last Play view). The panel scrolls: each image shows a portion of its content.

**Offline preview: synthetic game, answers and image; no AI calls, credentials, audio playback or device capture.** These are browser screenshots of the real App using explicitly labelled HTML stand-ins. Production injects `@decky/ui` controls and vertical/horizontal Focusable groups. Font/rendering/controller focus, installation, QAM notifications, audio routing and performance on Steam Deck remain **NOT RUN**. Keyboard/browser tests do not certify controller behavior.

The full viewport captures below show the surrounding review harness. Panel-only screenshots in the README are captured directly from the browser as well; neither version is a mockup. The right panel is the plugin. The left illustration and simulation buttons belong only to the review harness. Original opaque PNG branding from PR #2 is preserved; the compact menu symbol is a separately drawn matching SVG. [Asset sources](PRESENTATION_ASSETS.md). Browser tests also inspect a 360-pixel viewport and the menu symbol at 20/24/32 pixels.

## Play: a clear next step

Active game, readiness, one primary **Help me now** action, free question and the latest answer. The capture notice states the actual capability; the synthetic answer is explicitly based on notes, not a claimed observation of gameplay.

![English Play screen with active game and primary Help me now action](images/ui/01-play.png?raw=true)

## Game context

A game title and objective are enough to begin. Optional area, notes and AppID stay under Advanced options. Detection is unavailable in this offline harness, and manual entry remains available.

![Simple Game screen with title, objective and manual fallback](images/ui/02-game.png?raw=true)

## Welcome and guided setup

Original wordmark, short explanation and a Get started action. Setup does not send a remote request. The next image shows the first of three steps: game, AI service, then sharing permissions and an explicitly requested connection check that may cost money.

![First-use welcome with Decky Pilot wordmark](images/ui/03-onboarding.png?raw=true)

![First guided setup step with game fields](images/ui/09-guided-game.png?raw=true)

## Service and sharing

Credentials stay in Settings and inputs are empty in the preview. Chat context, image capability and manual image sharing have distinct controls; there is no silent recipient/model substitution. Selected model support is verified against official documentation, while access in an actual account remains untested.

![AI service credentials and explicit chat/image sharing settings](images/ui/04-service-sharing.png?raw=true)

## Independent languages

Interface and assistant language initially use English; complete Italian translation is available. Assistant language governs both answers and synthesized speech, independently of interface language. The legacy voice-language field is preserved in storage without overriding this decision.

![English interface and assistant language selectors with AI service settings](images/ui/05-languages.png?raw=true)

## Image review and recipient approval

The image is an explicitly labelled synthetic test fixture, not gameplay. The actual import flow validates and cleans images, previews the destination, and offers removal and per-image approval before analysis. **Help me now** cannot share an unapproved attachment. Native acquisition and automatic visual sharing remain unavailable because the verified Gamescope mechanism does not atomically bind acquisition to the authorized game.

![Synthetic image preview naming the recipient and requiring explicit approval](images/ui/06-image-review.png?raw=true)

## Pending request and cancellation

The harness deliberately delays a synthetic response to exercise the real pending/cancel layout. There is no real provider request or background capture.

![Pending question with a visible Cancel action](images/ui/07-pending.png?raw=true)

## Latest answer, voice and automatic state at 720 pixels

Full text remains readable, with Listen / Stop, a visible automatic-help state and secondary conversation access. Voice is unavailable in the offline harness; this screen does not demonstrate speech playback. Automatic help is off, and its information flow explains the unavailable capture capability.

![Scrolled Play view at 1280x720 with answer, Listen and Stop, automatic state and history](images/ui/08-play-720.png?raw=true)

## Voice settings

On-device voice is used only when an engine is already installed. OpenAI voice requires a separate key and explicit permission to send answer text, potentially incurring costs. Missing voice falls back to text; no engine is installed automatically.

![Voice enablement, service and volume settings](images/ui/10-voice.png?raw=true)

## Reproduction and historical assets

Run the existing MVP preview server, then `node scripts/capture_gallery.mjs`; ten full views, ten panel PNGs and commit/browser/time metadata are written under `artifacts/gallery/`. Use `PLAYWRIGHT_CHANNEL=chromium` on Linux. Source metadata is included alongside these images.

The eight earlier captures from `c60e6d7` were intentionally replaced. They remain in Git history and are not presented as the redesigned UI. Branding source commit `1b5cc03` was integrated into the MVP without merging either PR. PR #2 stays based on `codex/deckpilot-mvp`; no application code/dependency change is made here, and neither PR is merged.

Next hardware work follows the MVP branch's [hardware checklist](https://github.com/realfulvio/decky-pilot/blob/codex/deckpilot-mvp/docs/HARDWARE_VALIDATION.md) and [capture findings](https://github.com/realfulvio/decky-pilot/blob/codex/deckpilot-mvp/docs/CAPTURE_VERIFICATION.md): first establish a safe acquisition mechanism, then verify Deck ABI/install, actual controller/picker, popup/audio and performance. No unavailable Steam Deck is needed to reproduce these offline previews.
