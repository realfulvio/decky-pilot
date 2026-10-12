# Decky Pilot work checkpoint

Updated 13 October 2026. Resume here before the historical CODEX_HANDOFF.

## Authorization and scope

- Continue MVP PR #1 and gallery PR #2; preserve local changes and use normal commits/pushes. No merge, force push, history rewrite, Decky store publication or device installation.
- The owner now explicitly authorizes making `realfulvio/decky-pilot` PUBLIC after checking public files/history and completing current tests, build, packaging and CI. This supersedes the earlier private-only instruction.
- Publish only README, Italian translation, presentation images and presentation documentation on `main`. The MVP stays in PR #1; do not merge either PR.
- Finish an English-first GitHub presentation, matching Italian translation, actual browser gallery, clearly labelled concept illustrations, working relative links and rendered README QA.

## Starting state and resumed work

- MVP checkout: `codex/deckpilot-mvp`, initially `9f2a93c`; gallery: `docs/ui-gallery`, initially `eb6e2b8`. Both tracked/untracked working trees were clean. Existing ignored build/cache/artifacts are preserved.
- Both existing heads had green Linux CI. There was no checkpoint; CODEX_HANDOFF and PRODUCT_DECISIONS reconstructed the agreed scope.
- Review regressions reproduced before fixes: OpenAI discarded text on incomplete/max_output_tokens; mounted game/onboarding fields retained stale context. Fixes retain usable text without retry or budget increase and synchronize fields on context changes while preserving drafts during unchanged status polling.
- Added 12 backend and six frontend regression cases. Targeted checks pass. Full verification and final delivery evidence will be recorded below.
- Generated cover concept with the built-in image generation tool; public asset and provenance documentation are being prepared. No real device image, private screenshot or live provider call.

## Delivery verification

- Presentation-only main commit: `81b2a19`. Independently cherry-picked into MVP (`ac0b07b`) and gallery (`c6d12dc`); no merge, history rewrite or application code on main. Any README add/add conflicts were resolved using the reviewed presentation files; original application README remains as DEVELOPMENT.
- Gallery source `d192330cc36816c7e15d522932de0c1202c240d1`: ten full browser views plus ten direct panel screenshots, with browser/time/source metadata. Original branding preserved.
- Local checks: 146 backend passed without skips, 22 frontend, 13 tooling, six browsers; frozen install/lint/types/Ruff/zero-advisory audit/build/vendor/package all pass. 224 allowlisted package files. Final ZIP/source/checksums regenerate after each delivery commit.
- English/Italian README and gallery rendered from GitHub Markdown API output at 1200/390 pixels: all images decoded, 39 relative links resolve, no page overflow; visual review passed after stacking gallery images for phone readability.
- Reachable-history scan after presentation commits: 19 commits, 255 blobs, 32 distinct decoded raster images; no secret/private metadata finding. Eight historical screenshots were visually reviewed and contain only synthetic offline UI. Author identity is the existing public GitHub handle/noreply email. Repeat audit after final pushes.

## Final remote steps

Main presentation is pushed at `3db36bb` (33 presentation files, no application code). Gallery is pushed at `1083353`, based on the MVP. Both PRs are conflict-free; both original review threads are resolved after reproducing regression coverage. No merge commits exist. Shared gallery line endings were normalized to avoid an add/add review conflict. The public-history recheck covers 24 commits / 262 blobs / 32 decoded raster images. Final Linux runs are in progress; query current GitHub checks rather than assuming a previous head covers this one.

1. Push normal commits to MVP/gallery/main, update existing PR metadata and verify final Linux CI (including isolated extracted-package runtime).
2. Repeat reachable-history audit for all final refs.
3. After checks pass, set visibility PUBLIC using existing explicit owner authorization and verify anonymous README/assets. Record resulting visibility/evidence here.

Hardware validation remains NOT RUN: safe atomic game-only capture, Deck ABI/install/controller/picker/QAM/audio/performance. Production capture remains disabled. Optional live credentials/account smoke is deferred.
