# Publication review

Review date: 13 October 2026. The owner explicitly authorized public visibility after verification, and presentation-only publication on main without merging the MVP. No Decky store publication, release or device installation is included.

## Scope

The review covers all Git objects reachable from local/remote branches and tags, current presentation files, commit authors/messages, original and historical images, PR/review text and CI deliverables. This repository's only commit author uses the owner's existing public GitHub identity and GitHub noreply address. No private account email or connection credential is added. Historical workstation paths refer to the generic Admin workspace, not passwords or keys.

The automated scanner checks private keys, OpenAI/Anthropic/Google tokens, GitHub tokens, AWS access key identifiers, Slack tokens, credential-bearing URLs and accidentally tracked runtime/cache filenames. It decodes historical raster images and checks embedded EXIF/GPS/comment metadata. It suppresses matching values. This is a targeted scan, supported by manual source/path/image review; it does not claim mathematical proof that arbitrary private data cannot exist.

Current and historical UI images are synthetic offline browser views. The cover depicts an original fictional game and unbranded handheld; it is explicitly labelled concept artwork. Original branding is owner-provided. No real gameplay, account, desktop or private screenshot is used. Build outputs, caches, credentials and temporary QA renders remain ignored/untracked outside the public deliverables.

## Publication boundaries

- Main contains only README, Italian translation, brand/presentation images, UI gallery and presentation documentation. No backend, frontend, dependencies, plugin package, test harness or application code is integrated there.
- MVP code remains in PR #1; the gallery is coordinated in PR #2. Both stay open and unmerged.
- Full lint/types/frontend/tooling/backend/browser, audit, build/vendor/package and extracted Linux package smoke are required on the final MVP PR checks. Main's presentation is verified independently for working relative links, PNG decoding, provenance and rendered README layout.
- Actual Steam Deck ABI/install/controller/picker/QAM/audio/performance and safe atomic capture remain NOT RUN. Production direct/automatic capture remains disabled.

The final counts, current CI links, repository visibility and delivery commits are recorded in the MVP branch's WORK_CHECKPOINT and TEST_PLAN. The visibility change happens only after the complete audit and verification pass; this document records the process without pretending an earlier check covered later objects.
