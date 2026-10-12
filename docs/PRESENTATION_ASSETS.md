# Presentation asset sources

Reviewed 13 October 2026. All presentation assets are committed in this repository and use relative README links. No private image, credential or account screenshot is included.

| Asset | Type / provenance | What it demonstrates |
|---|---|---|
| `assets/brand/decky-pilot-logo-dark.png`, `decky-pilot-icon-dark.png` | Owner-supplied original branding from `1b5cc03`; original bytes preserved | Brand identity, not hardware evidence |
| `assets/brand/decky-pilot-menu.svg` | Original editable, hand-drawn menu mark | Compact brand symbol |
| `assets/presentation/cover-concept.png` | Original built-in image generation output | Concept artwork: fictional unbranded handheld/game |
| `assets/presentation/cover.png` | Built-in image generation edit with typography | Concept cover, visibly labelled hardware validation pending |
| `assets/presentation/how-it-works-en.svg`, `how-it-works-it.svg` | Editable SVG illustrations authored for this presentation | Manual import/approval flow; not screenshots |
| `docs/images/ui/*.png` | Actual Microsoft Edge screenshots of committed React App `d192330cc36816c7e15d522932de0c1202c240d1` | Ten full browser views plus ten directly captured panels; synthetic game/answer/image, HTML controls, no provider call/device/audio |

There are no photorealistic product mockups in this delivery. The AI cover is a concept, the workflow is an illustration, and the UI gallery contains actual offline browser screenshots. No image is evidence of Steam Deck installation or compatibility.

## Regenerate browser screenshots

Use the MVP branch and start its offline preview server. Then run `node scripts/capture_gallery.mjs` (Windows: installed Edge; Linux: `PLAYWRIGHT_CHANNEL=chromium`). Copy the twenty PNGs and `source.json` from `artifacts/gallery/` into `docs/images/ui/`. The script records its committed source revision, browser and UTC capture time. Full views use 1280x800 or 1280x720; panels are direct locator screenshots of the same rendered page. Never replace these with device claims or real accounts.

## AI cover prompts

Built-in image generation was used, without a CLI/API-key fallback. Original output is preserved alongside the final cover. Prompts contain no private data; service results can vary on regeneration.

### Original concept

```text
Use case: stylized-concept. Asset type: GitHub repository cover illustration for Decky Pilot, a consent-first AI gaming companion. Create a sophisticated wide 16:9 editorial illustration, dark midnight navy and teal with small warm amber accents, premium cinematic depth and delicate grain. An original unbranded handheld gaming device floats at the right, showing a fictional minimalist game world: luminous doorway, mountains and one small player. From an abstract screenshot card to a speech waveform, a fine mint path suggests optional image understanding and voice. The left half is spacious navy negative space for typography to be added separately. The device is conceptual, no Steam or Valve branding, no commercial game characters, no real app UI, no hands or people, no credentials, no accounts. Crisp elegant composition suitable for software README, captivating yet restrained. No text, no letters, no watermark. This is concept artwork, not a photograph or proof of any working hardware.
```

### Typography edit

Input: `assets/presentation/cover-concept.png`.

```text
Use case: precise-object-edit. Asset type: polished GitHub README cover. Edit the attached original conceptual cover: preserve the original unbranded handheld, fictional game, floating image and voice-waveform cards, colors and artistic background. Add precise beautifully typeset editorial typography in the spacious left half. Small mint eyebrow "DECKY PILOT", large warm-white headline on three lines exactly "Your next move,
made clearer.", small white subheading on two lines exactly "Game help. Approved images.
Optional voice.", and a small understated bottom-left caption exactly "CONCEPT ART • HARDWARE VALIDATION PENDING". Modern sans serif, excellent kerning, strong hierarchy and high contrast. Maintain wide composition and generous margins, no badges or extra logos. These are concept visuals and cannot imply a real Steam Deck test. Do not change the illustration, do not add app UI, no watermark.
```

## Presentation review

Both READMEs and the gallery must pass relative-link/image decoding checks and rendered visual review at desktop and narrow widths. The cover's English headline is translated in README.it.md text. Technical docs remain on the MVP branch; main contains presentation only. Application license and third-party notices are available on that branch. Keep original branding intact when making variants.
