# Decky Pilot work checkpoint

Resume here before historical CODEX_HANDOFF. Current extension supersedes earlier completion claims.

## Steam Deck run, 17 October 2026 (latest)

The owner authorized unattended device testing over SSH until 03:00 CEST, then a repository update. Their absolute constraint is the safety of the Steam account. Device: Steam Deck LCD, SteamOS 3.8.28, Decky Loader 3.2.10 (CPython 3.11). Results are in HARDWARE_VALIDATION, the capture environment finding in CAPTURE_VERIFICATION, and the anti-cheat and ToS analysis in ACCOUNT_SAFETY.

- Fixed `prepare_capture` to report `CAPTURE_UNAVAILABLE` before guard checks, plus a Decky-environment regression.
- Fixed espeak-ng streamed WAV placeholder sizes, with a regression on the bytes captured on the Deck.
- Added DP-026 (competitive-play guard before release) and DP-027 (upstream Decky SIGKILL on stop).
- The final build with these fixes is left installed on the Deck with empty data. Test images, logs, caches and the 15 October temporary plugin's leftovers were removed. Its panel appears after the next Steam/Deck restart (frontend import events were not delivered during the run).
- The CachyOS mini PC was not used. It also has the owner's Steam account, so the same rules apply there.
- Next: owner-present visual/controller/audio pass, game detection with a single-player title chosen by the owner, then DP-026 before any release. No game may be launched remotely.

## Current scope and implementation

Existing workspace `C:/Users/Admin/deckpilot`, branch `codex/deckpilot-mvp`; gallery worktree
`C:/Users/Admin/deckpilot-gallery`, branch `docs/ui-gallery`; presentation worktree
`C:/Users/Admin/deckpilot-presentation`, branch `main`. Preserve ignored caches/artifacts.
Repository is already PUBLIC with the owner's explicit authorization. No merge, force push, store,
release or device install. Main is presentation-only; application stays in PR #1, gallery in PR #2.

Browser capture source `205a861f423678fb2cefde0b287df9ae6c6ee070` includes native ChatGPT plan OAuth,
separate advanced OpenAI key, Claude/Gemini/Grok/Ollama, account/service-returned catalogs,
bounded documented pagination, exact image gates, refresh/revoke/limits and structured visual context.
Own backend credentials only; no cookies/other-app secrets or paid/provider fallback.
Help me now combines the player's question, confirmed game and recent approved image;
observations/deductions and one clarification are distinct. Four bounded clarification replies remain
session context beyond the rolling history; game change/clear/delete removes them. The final
follow-up also refuses a clarification already answered among the retained pairs, even after
another intervening question; its reproducing regression passes.
Auto admission >=90 seconds; stale frames >45 seconds, overlaps, duplicates, menu/loading and
ambiguity are refused/suppressed. Manual corrections survive until actual game switch.
Loopback integration exposed and fixed Python 3.13 callback shutdown deadlock; test uses fake identity.

**Central unresolved blocker:** Gamescope command adapter exists but cannot atomically bind capture
to the authorized game during transitions. `CAPTURE_SAFETY_VALIDATED=False`; production automatic
and direct capture remain disabled. Manual import is an alternative, not completion. No Steam Deck
available; no install/controller/browser/audio/capture hardware test run. No real account grant,
catalog, refresh/revoke, paid inference, plan eligibility or live model-quality test run.

## Verification and presentation

Local checks: 182 backend passed / two Linux-only process checks skipped on Windows; 27 frontend;
13 tooling; six browser. ESLint/types/Ruff/build pass. JS audit and OSV for five shipped Python pins
report zero advisories. Vendor/package pass with 435 allowlisted files. Final committed source ZIP
and installable ZIP/checksums regenerate after delivery commits. Linux CI must verify extracted
CPython 3.11 Pillow/PyJWT/cryptography/RSA/lifecycle, plus the platform-specific tests.

Commands: `corepack pnpm verify`; `.venv/Scripts/python.exe -m ruff check backend main.py scripts tests/backend`;
`.venv/Scripts/python.exe -m pytest -q --basetemp artifacts/pytest-context`;
`corepack pnpm exec playwright test`; `node scripts/audit.mjs`;
`.venv/Scripts/python.exe scripts/audit_python.py`; `scripts/vendor.py`; `scripts/package.py`;
`scripts/verify_package.py`; Linux only `scripts/verify_package.py artifacts/deckpilot-0.1.0.zip --runtime`.
Stop Vite before backend tests on Windows (watcher interference with atomic temporary writes).

15 actual browser views plus 15 direct panel captures from committed source 205a861 (metadata
in docs/images/ui/source.json). Synthetic data/replies; capture capability explicitly simulated only
for consent UI. No live auth/inference/capture/speech. New built-in imagegen cover is labelled concept;
original branding/earlier art retained. Editable EN/IT workflow. README EN/IT, gallery, provider billing,
privacy, status table and hardware blockers updated. GitHub Markdown API render at 1200/390px:
all images decoded, no page overflow; 54 relative links and 35 current PNGs verified. Manual visual
review covers cover, diagrams, contextual steps, onboarding and mobile layout.

## Publication and current verification

Public main is `c574cf5`: exactly 47 presentation-only files, LF-identical to shared MVP files,
no application code. English repository description and both existing PRs updated. Gallery was
brought to the same MVP tree with a normal commit preserving history; only GALLERY_REVIEW differs
between current trees. Three-dot GitHub comparison can show inherited changes because histories
diverge; no merge/rewrite was used. PRs are open and conflict-free.

Published EN/IT README pages checked anonymously at 1200/390px: HTTP 200 and all 12 images load.
Actual page screenshots inspected. Source/history audit at this delivery: 39 commits, 379 blobs,
59 distinct decoded historical/current rasters, no finding. Original image metadata and branding
preserved; no private credentials/account/gameplay used. Caches/temporary files remain ignored.

Full Linux checks passed on MVP `90958cf` [PR 38320636675](https://github.com/realfulvio/decky-pilot/actions/runs/38320636675)
and [push 38320631917](https://github.com/realfulvio/decky-pilot/actions/runs/38320631917), plus gallery
`c32b527` [38320642211](https://github.com/realfulvio/decky-pilot/actions/runs/38320642211).
These passed 184 backend tests without skips, 27 frontend, 13 tooling, six browser, audits and
extracted cryptographic/Pillow runtime on their listed heads. Final clarification/documentation
follow-up must also pass [current MVP checks](https://github.com/realfulvio/decky-pilot/pull/1/checks)
and [current gallery checks](https://github.com/realfulvio/decky-pilot/pull/2/checks); older runs do not
certify a later head. Review ZIP/source/checksums are workflow artifacts, not a release.

Remaining work requires external inputs: eligible account/dedicated API credentials for real provider
acceptance, and actual Steam Deck for hardware acceptance. Establish atomic game-only acquisition
before enabling the capture gate. No ordinary technical decision or publication permission is pending.

Initial extension CI on 903b080 passed [PR run 38318741305](https://github.com/realfulvio/decky-pilot/actions/runs/38318741305)
and [push run 38318736988](https://github.com/realfulvio/decky-pilot/actions/runs/38318736988).
These cover that earlier source only. Current-head checks remain authoritative.

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
