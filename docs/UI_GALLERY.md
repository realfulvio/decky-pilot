# Decky Pilot interface gallery

These are **actual browser screenshots of the implemented React App**, with labelled HTML stand-ins and synthetic data. They are not mockups, Steam Deck captures, live AI answers or hardware evidence. The offline harness does not sign in, send paid requests, acquire gameplay or play speech. Production injects Decky controls; controller acceptance remains **NOT RUN**.

[source.json](images/ui/source.json) records the committed source, browser and UTC capture time. Fifteen full views and fifteen directly captured panels are included. The left illustration and simulation buttons are review-harness content; the right panel is the application. [Asset provenance](PRESENTATION_ASSETS.md).

## Help me now

The game, primary action, question and latest reply stay together.

![Actual browser Help me now view with synthetic context](images/ui/01-play.png?raw=true)

## Contextual next steps

Synthetic observations and deductions are explicitly separated, followed by concrete steps. This demonstrates the layout and result contract, not model accuracy.

![Actual browser contextual answer with synthetic observations, deductions and steps](images/ui/15-contextual-answer.png?raw=true)

## One clarification

A synthetic ambiguous scene produces one short question. The player's answer becomes bounded session context.

![Actual browser one-question clarification](images/ui/13-clarification.png?raw=true)

## Game identification and correction

Use available Steam information, confirm/correct the title or enter an unknown/non-Steam game manually. This offline harness has no actual running Steam game.

![Actual browser game context form](images/ui/02-game.png?raw=true)

## Welcome and onboarding

![Actual browser welcome](images/ui/03-onboarding.png?raw=true)

![Actual browser guided game setup](images/ui/09-guided-game.png?raw=true)

## Choose your AI

ChatGPT plan access and advanced OpenAI developer API access are separate connections. Claude, Gemini, Grok and Ollama remain choices. Model names come from the selected service, with independent image gates.

![Actual browser AI connection selection](images/ui/11-ai-connection.png?raw=true)

## ChatGPT sign-in settings

This screenshot shows the real account-setup controls with **no connected account**. It does not demonstrate successful authorization. Real account eligibility and SteamOS browser/loopback behavior remain untested.

![Actual browser ChatGPT setup with no account](images/ui/14-chatgpt-sign-in.png?raw=true)

## Separate capture and sending permissions

**Capture availability is simulated only to show this implemented consent dialog. No screen is acquired.** Production capture stays disabled until safe atomic game-only acquisition is established.

![Actual browser capture consent with simulated availability](images/ui/12-capture-consent.png?raw=true)

The import alternative independently validates and cleans an explicitly selected PNG/JPEG, previews the recipient and requires per-image sending approval. It does not complete automatic gameplay capture.

![Actual browser synthetic image preview and recipient approval](images/ui/06-image-review.png?raw=true)

## Service permissions and independent languages

Inputs contain no credentials. Game-context sharing, images, capture and Speech have separate permissions. Interface language and assistant/voice language are independent; English defaults and complete Italian translation are retained.

![Actual browser service sharing settings](images/ui/04-service-sharing.png?raw=true)

![Actual browser independent language settings](images/ui/05-languages.png?raw=true)

## Pending and cancellation

The harness deliberately delays a synthetic answer; no provider request is made.

![Actual browser pending request and Cancel](images/ui/07-pending.png?raw=true)

## Voice and automatic state

Listen/Stop and automatic status are real controls. These previews do not play speech or demonstrate hardware capture. Local voice needs an installed engine; online Speech requires a separate OpenAI API key and permission, even with ChatGPT plan sign-in.

![Actual browser Play controls at 1280x720](images/ui/08-play-720.png?raw=true)

![Actual browser voice settings](images/ui/10-voice.png?raw=true)

## Reproduce and validate

On the MVP branch, start `corepack pnpm preview`, then run `node scripts/capture_gallery.mjs`. Windows uses installed Edge; Linux uses `PLAYWRIGHT_CHANNEL=chromium`. The script creates 30 PNGs and source metadata in ignored `artifacts/gallery/`. Full views use 1280x800 or 1280x720; panels are browser locator captures, not fabricated afterward.

Older gallery images remain in Git history, clearly superseded. Original branding bytes are preserved. The concept cover and editable workflow are separately labelled illustrations. Main contains presentation only; code remains in [PR #1](https://github.com/realfulvio/decky-pilot/pull/1), with this gallery coordinated in [PR #2](https://github.com/realfulvio/decky-pilot/pull/2). Neither PR is merged.

Hardware work follows the [device checklist](https://github.com/realfulvio/decky-pilot/blob/codex/deckpilot-mvp/docs/HARDWARE_VALIDATION.md) and [capture blocker](https://github.com/realfulvio/decky-pilot/blob/codex/deckpilot-mvp/docs/CAPTURE_VERIFICATION.md). Browser/keyboard checks cannot certify controller, SteamOS browser callbacks, QAM, audio or performance.
