# Decky Pilot work checkpoint

Updated 14 October 2026. Resume here before the historical CODEX_HANDOFF.

## Active extension — situation-aware assistant and account catalogs

Latest user instructions extend the delivered MVP; do not restart. Repository is already PUBLIC.
MVP checkout remains `C:/Users/Admin/deckpilot` on `codex/deckpilot-mvp`; gallery worktree
`C:/Users/Admin/deckpilot-gallery` on `docs/ui-gallery`; presentation worktree
`C:/Users/Admin/deckpilot-presentation` on `main`. All started clean; other worktrees remain clean.

In-progress uncommitted code: official OSS ChatGPT OAuth (127.0.0.1 listener, PKCE/state/nonce,
issued dynamic client, PyJWT/JWKS/issuer/audience/expiry verification, separate account records,
serialized rotating refresh and revocation), separate ChatGPT provider using public Responses SSE
with store=false, stream=true and no unsupported output budget; native Grok/xAI Responses and
language-model catalog/modalities; credential-scoped catalogs for all providers; no static GPT-4.1
picker. Exact documented image allowlist remains conservative for providers lacking modalities.
Tokens never returned in status, no browser cookies or other-app credential reads, no paid fallback.
Contextual JSON estimates separate observations/inferences, one clarification, answer in session
history; visual output must validate, automatic output must be structured and suppress menus,
loading, ambiguity and useless results. Prepared images expire for sending after 45 seconds.
Manual title correction is retained until an observed game switch. Existing capture safety gate stays
disabled: game-only acquisition is not atomic; hardware/integration validation remains NOT RUN.

Local checks currently pass: `corepack pnpm verify` (lint/types, 25 frontend, 13 tooling, build),
`.venv/Scripts/python.exe -m ruff check backend main.py scripts tests/backend`,
`.venv/Scripts/python.exe -m pytest -q --basetemp artifacts/pytest-account` (178 pass, two Linux-only
process checks skipped on Windows). Five shipped Python pins have zero OSV advisories.
Auth Linux wheels are hash-pinned in contracts/auth-wheels.json and vendored by scripts/vendor.py;
extracted ZIP CI now verifies real RSA JWT signing/verifying as well as Pillow/lifecycle.

Next: finish auth/capture edge review and tests, generate updated actual browser gallery and workflow,
rewrite README EN/IT/provider verification docs, inspect rendered pages, audit history/assets, commit
and push normal commits on existing branches, copy only presentation/docs/assets to main, update
both PRs and repository English description, verify latest Linux CI/package artifacts. No merge/store.
New concept cover generated with built-in imagegen is saved as assets/presentation/cover-v2.png;
original branding and previous cover retained. No live account/API/hardware tests have run.

Historical completion statements below refer to the earlier scope and are superseded by this extension.

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

## Completed remote delivery

Main presentation is pushed at `3db36bb` (33 presentation files, no application code). Gallery is pushed at `1083353`, based on the MVP. Both PRs are conflict-free; both original review threads are resolved after reproducing regression coverage. No merge commits exist. Shared gallery line endings were normalized to avoid an add/add review conflict. The public-history recheck covers 24 commits / 262 blobs / 32 decoded raster images. Final Linux runs are in progress; query current GitHub checks rather than assuming a previous head covers this one.

- Repository visibility changed to **PUBLIC** on 13 October 2026 after green current MVP PR/push runs [38315477004](https://github.com/realfulvio/decky-pilot/actions/runs/38315477004) / [38315471465](https://github.com/realfulvio/decky-pilot/actions/runs/38315471465) on `d613d77`, plus gallery [38315386247](https://github.com/realfulvio/decky-pilot/actions/runs/38315386247) on `1083353`. Full Linux checks pass: 146 backend, 22 frontend, 13 tooling, six browsers, clean audit, presentation verification, build/vendor/package and isolated extracted ZIP runtime. Artifacts uploaded. Gallery combined archive has its additional review doc (225 files); MVP has 224.
- Anonymous actual GitHub page checks pass for English/Italian at 1200/390 pixels: HTTP 200, all nine README images loaded. Relative image URLs now explicitly request raw responses; local links/provenance/PNG checks still pass. Verification uses a fresh page URL to avoid cached private-era responses. Temporary diagnostics remain ignored.
- Main stays presentation-only (33 files), no application code. Shared SVG workflow files include intrinsic dimensions for full-width rendering. Both PRs remain open/unmerged; no release, store publication or device install.
- Final documentation/asset-link/verification-source commits require their own green current CI. Do not confuse recorded successful prerequisite runs with subsequent heads; GitHub current checks are authoritative. No further implementation work is required for this authorized offline scope.

Final verification on `ead68e5` passed [MVP PR CI 38315934418](https://github.com/realfulvio/decky-pilot/actions/runs/38315934418) and [push CI 38315928211](https://github.com/realfulvio/decky-pilot/actions/runs/38315928211); gallery head `e196c7d` passed [38315935922](https://github.com/realfulvio/decky-pilot/actions/runs/38315935922). Final main head is `dd8c222`. Public history recheck: 30 commits, 274 blobs, 32 distinct decoded raster images, no finding. All three checkouts are clean and synchronized; zero merge commits. The delivered README/assets were inspected on actual anonymous GitHub pages. This evidence-only checkpoint follow-up also requires its own green [current MVP checks](https://github.com/realfulvio/decky-pilot/pull/1/checks); [gallery checks](https://github.com/realfulvio/decky-pilot/pull/2/checks) remain authoritative for that head. Authorized delivery is complete; remaining hardware/live-account work is explicitly deferred.

Hardware validation remains NOT RUN: safe atomic game-only capture, Deck ABI/install/controller/picker/QAM/audio/performance. Production capture remains disabled. Optional live credentials/account smoke is deferred.
