# Presentation asset sources

All presentation assets are committed and use working relative links. No private gameplay, account, desktop, credential or personal screenshot is included.

| Asset | Type / provenance | Meaning |
|---|---|---|
| Original dark logo/icon PNGs in `assets/brand/` | Owner-supplied original branding from `1b5cc03`; bytes preserved | Brand identity; no device proof |
| `assets/brand/decky-pilot-menu.svg` | Original editable menu mark | Compact identity |
| `assets/presentation/cover-v2.png` | Built-in image generation output | Concept: fictional unbranded handheld, puzzle, screen consent, clarification and voice |
| Earlier `cover-concept.png`, `cover.png` | Original generated concept and typography edit, retained | Earlier artwork; not product screenshots |
| `how-it-works-v2-en.svg`, `how-it-works-v2-it.svg` | Editable authored SVG diagrams | Intended game → Help me now → separate permissions → recent context → steps/question/voice flow |
| Earlier `how-it-works-en.svg`, `how-it-works-it.svg` | Retained editable diagrams | Earlier manual-import illustration |
| `docs/images/ui/*.png` | 15 full browser views and 15 directly captured panels; commit/time/browser in [source metadata](images/ui/source.json) | Implemented React App, synthetic data and HTML stand-ins; no live account/inference/capture/speech |

The cover is visibly labelled concept artwork and hardware validation pending. The workflow is a diagram. UI gallery images are real browser captures, with capture availability explicitly simulated for the permission dialog. None proves Steam Deck compatibility.

## Generation and reproduction

Built-in imagegen was used, without API-key or CLI fallback. The v2 prompt requested a polished midnight-navy/teal/amber editorial cover for **Decky Pilot**: an original unbranded fictional handheld puzzle, a consent card, a short clarification and voice waveform; English product-goal typography; clearly labelled concept and hardware validation pending; no commercial game characters, personal data, accounts or real device photographs. Generated raster saved as `cover-v2.png`; no screenshot was passed off as source evidence.

Earlier cover prompts requested the same fictional handheld/game treatment and a separate typography edit (“Your next move, made clearer.” / “Game help. Approved images. Optional voice.”). Their original raster assets are retained.

To reproduce screenshots, start the MVP offline preview and run `node scripts/capture_gallery.mjs`, then copy the 30 PNGs and `source.json` from ignored `artifacts/gallery/`. Windows defaults to Edge; Linux uses `PLAYWRIGHT_CHANNEL=chromium`. Do not add real account screens, credentials or private gameplay.

## Visual review

Both README languages and the complete gallery are rendered using GitHub Markdown API output at desktop and phone widths, with relative-link and image-decoding checks. The published English and Italian GitHub pages are also checked anonymously. English cover typography has an Italian text equivalent in README.it.md. Main contains only presentation; application license and technical documentation remain on the MVP branch.
