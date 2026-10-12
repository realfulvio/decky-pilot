# Deferred Steam Deck validation

**NOT RUN: Steam Deck unavailable.** No installation on the mini PC or any substitute device. Source review, mock processes, DOM previews and Linux CI do not certify Gaming Mode.

Record date/operator, LCD/OLED model, SteamOS/kernel/glibc, Steam client/channel, Decky version/commit, Python ABI, DeckPilot commit/ZIP SHA256, UID/GID/settings/runtime ownership, and installed espeak-ng/provider/model/Ollama versions. Never record keys. All target fields are currently NOT RUN.

| Done | Test / measurable acceptance | Evidence |
|---|---|---|
| [ ] | ZIP install/load/upgrade/uninstall; vendored Pillow ABI; reversible install; no leftover tasks | NOT RUN / DP-015 |
| [ ] | Real Decky rendering at 1280x800/720; readable text, scroll, no clipped controls | NOT RUN / DP-015 |
| [ ] | Controller/virtual keyboard, onboarding, focus after dropdowns/picker, Cancel and Stop reachable | NOT RUN / DP-015 |
| [ ] | Full English/Italian UI; independent response/voice languages retained across reload | NOT RUN / DP-021 |
| [ ] | Steam/non-Steam/unknown/multiple-app detection; changes reject stale results | NOT RUN / DP-015 |
| [ ] | Six-second popup with QAM open/closed, full answer retained, dismiss on game change/unload | NOT RUN / DP-015 |
| [ ] | Dedicated picker root, actual cleaned preview, destination approval/revocation, no background file reads | NOT RUN / DP-015 |
| [ ] | Capture stays unavailable until atomically safe targeting; race/refusal tests from CAPTURE_VERIFICATION | NOT RUN / DP-016 |
| [ ] | Once safe capture exists: separate session consent/visible indicator/immediate pause, >=90s, useful context only, dedup/error/budget controls | NOT RUN / DP-016 |
| [ ] | Local/remote synthetic voice, absent engine/text fallback, IPC payload, cancel/Stop | NOT RUN / DP-015 |
| [ ] | Speakers/headphones/Bluetooth, volume/routing/game audio, no residual playback | NOT RUN / DP-015 |
| [ ] | Offline/denied provider/rate limit/unreachable Ollama: safe errors/manual retry/no silent fallback | NOT RUN / DP-015 |
| [ ] | Actual 0700/0600 ownership, no secret/content logs, consistent deletion/retention | NOT RUN / DP-015 |
| [ ] | CPU/RAM idle, latency/frame rate and sleep/resume; report tools/method/real measurements | NOT RUN / DP-017 |

Use sanitized synthetic evidence and reproducible issues for failures. Do not tick hardware rows based on tests/build. Live API smoke is separate, optional and requires explicit consent and dedicated credentials. Hardware availability is not required to complete offline review and CI.
