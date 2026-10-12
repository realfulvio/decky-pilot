# Decky Pilot — brand assets

The public product name is **Decky Pilot**, as requested by the owner on 12 October 2026. The GitHub repository is now `realfulvio/decky-pilot`; existing technical identifiers remain `deckpilot`/`DeckPilot`; changing the display name must not discard saved settings, keys or history.

## Assets

![Decky Pilot wordmark](../assets/brand/decky-pilot-logo-dark.png)

![Decky Pilot icon](../assets/brand/decky-pilot-icon-dark.png)

- Horizontal logo: `assets/brand/decky-pilot-logo-dark.png`.
- Square symbol: `assets/brand/decky-pilot-icon-dark.png`.
- PNG raster assets generated with built-in ImageGen; these selected versions have an opaque dark background, not transparency.
- Identity: handheld gaming device, forward navigation chevron, mint/teal, white and navy.
- Intended colors: teal `#21E6C1`, white `#FFFFFF`, navy `#0B1320`. Generated pixels may vary slightly from these target values.

The original wordmark PNG is integrated into README and onboarding; the original square icon PNG is preserved intact. A separate hand-drawn `decky-pilot-menu.svg` matches the console/chevron identity and supplies the menu and compact panel mark. It is a new vector drawing, not a converted/relabelled PNG. Browser rendering was inspected at 20, 24 and 32 pixels on navy; actual Decky hardware rendering remains deferred.

## Integration task for the implementation branch

Use **Decky Pilot** in the visible plugin name, headings, onboarding and English public documentation. Integrate the logo into the README and onboarding; use the symbol alone for menu/icon surfaces. Provide accessible alt text and maintain legible sizing. Preserve existing internal identifiers/storage paths unless a tested migration is necessary. Do not rename the repository, break the remote, discard keys or rename the working branch as a side effect. Keep existing Italian strings as translations while English becomes the default UI.

Source commits `c60e6d7` (historical gallery) and `1b5cc03` (original raster branding) were verified on PR #2. The branding-only commit was cherry-picked into the MVP and integrated without merging either PR. Gallery images are regenerated separately from committed MVP screens; original asset bytes and generation prompts are preserved. The old integration task above records the source guidance; the implementation now satisfies it while preserving manifest/storage identifiers.

## Generation prompts

Tool: built-in ImageGen, not a CLI/API script.

### Horizontal logo

```text
Design a polished original production logo for the gaming AI companion app 'Decky Pilot'. Use a perfectly uniform opaque dark navy background #0B1320, no transparency. Horizontal logo lockup: on left a simple bold mint-teal handheld console silhouette, with a white forward navigation chevron centered in the dark screen, minimal circular controls and a compact plus sign; on right exact text 'Decky Pilot' in pure white clean bold rounded geometric sans serif. Text must be razor crisp solid continuous shapes, professionally typeset with excellent kerning and correct spelling, absolutely no distressed/grunge/broken lettering. Symbol feels like a helpful gaming navigator, approachable, legible at small size. Flat vector-style fills, clean sharp smooth edges. Teal #21E6C1, white #FFFFFF, navy #0B1320 only. Balanced wide composition, ample clean margins around centered logo. No gradients, texture, glow, shadows, noise, 3D, mockup, extra text or watermark. Original mark, do not imitate any existing Steam/Valve/Decky corporate logo. Finished high-quality brand logo, not a concept sheet.
```

### Square icon

The horizontal logo was supplied as an identity reference.

```text
Create a matching square app icon for Decky Pilot using the handheld-and-chevron symbol in this logo as identity reference. Only the symbol, absolutely NO text or lettering. Square canvas with opaque dark navy #0B1320 background, centered bold teal handheld silhouette with a white forward chevron inside a dark navy screen. Simplify controls to a minimal circle and plus on left, circle and short rounded dash on right, bold enough to read at 24 pixels. Flat clean crisp continuous shapes, smooth precise corners, no texture, gradients, shadows, glow or distressed edges. Generous equal padding, symbol fills about 75 percent canvas width. Preserve teal/white/navy identity from reference. Finished minimal recognizable menu icon.
```
