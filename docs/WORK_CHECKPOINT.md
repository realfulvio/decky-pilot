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

## Remaining delivery work

1. Regenerate browser gallery from committed fixed source; preserve original branding.
2. Finish README EN/IT, presentation images/docs and rendered desktop/narrow QA.
3. Audit all reachable Git blobs, metadata and image provenance for secrets/private content; resolve safely without rewriting history.
4. Complete local checks/package, push MVP/gallery/presentation-only main, update existing PRs and verify final CI.
5. Only after checks pass, set repository visibility PUBLIC and verify anonymous access. Record final evidence here.

Hardware validation remains NOT RUN: safe atomic game-only capture, Deck ABI/install/controller/picker/QAM/audio/performance. Production capture remains disabled. Optional live credentials/account smoke is deferred.
