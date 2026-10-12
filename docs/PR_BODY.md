# Decky Pilot MVP: guided English-first UI and safe visual assistance

Decky Pilot now offers a simple Play screen with the active game, Help me now, a free question, the latest full answer and voice controls. Guided onboarding moves provider/model/keys/permissions into Settings. Production uses real Decky components; shared complete English/Italian catalogs provide independent interface and assistant language choices, with assistant language governing responses and speech, initially English.

Manual gameplay image import is cleaned, previewed and approved for the chosen recipient before native OpenAI/Claude/Gemini/Ollama analysis. Prompts distinguish visible observations from guesses and do not invent hidden progress, inventory or missions. Voice reads unchanged text with the assistant language and separate remote consent.

Source verification found a real Gamescope screenshot command and a bounded adapter is implemented. However, it has no atomic game-window binding, so production capture remains unavailable to prevent account/key screen acquisition. Manual import works. Separate per-session automatic visual consent/status/pause, >=90-second cooldown and useful-context/dedup/error/budget controls are implemented and tested; activation stays blocked until safe acquisition is validated. See CAPTURE_VERIFICATION and the explicit NOT RUN hardware checklist.

The high braces advisory is resolved by removing the vulnerable build chain and replacing cleanup with confined Node filesystem operations. The audit exemption is removed; zero advisories were reported and all checks remain enabled. Linux CI validates actual extracted ZIP/native Pillow/backend lifecycle in an isolated CPython 3.11 process.

Validation: 16 frontend, 13 tooling, 132 Python passed locally (two Windows-only symlink skips), six browser tests at 1280x800/720 including narrow panels, Italian, small-icon branding and image consent; lint/types/Ruff/secret scan/audit/build/vendor/package. Linux CI evidence is in TEST_PLAN and this PR's current checks. All provider/capture fixtures are synthetic; no real credentials/live calls/device installation.

Existing [gallery PR #2](https://github.com/realfulvio/decky-pilot/pull/2) is coordinated with English previews from the same new screens and remains based on this MVP branch. Neither PR is merged. Next steps: review, obtain safe atomic capture targeting, then actual Deck ABI/controller/picker/popup/audio/performance validation when hardware becomes available.

Branding from existing PR #2 is integrated: original wordmark/icon PNGs, logo in README/onboarding, compact Decky Pilot identity and a separate matching hand-drawn SVG menu symbol. Technical identifiers/storage remain compatible. Official-docs image model catalog is shared with backend admission; undocumented cloud models cannot receive images. English issue templates/package metadata and PRODUCT_DECISIONS addendum match the final product.

Verified [Linux branding CI](https://github.com/realfulvio/decky-pilot/actions/runs/38311241604) on `c27050bef0c4b59a0019e382b166669d251b4059`: 134 Python tests without skips, 16 frontend, 13 tooling, six browser tests, zero advisories, build and actual extracted ZIP runtime; artifact uploaded. Documentation/gallery updates also require green current checks. Ten English previews with source metadata replace the historical gallery in PR #2.
