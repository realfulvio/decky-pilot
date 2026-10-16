# Steam Deck validation

**First plugin installation on a Steam Deck: 17 October 2026, 01:08–01:30 CEST.** (A read-only compositor protocol probe, without installing anything, ran on 13 October on the parallel `codex/decky-pilot-safe-capture-20261013` line.) Backend, packaging, storage and lifecycle checks ran on an actual Steam Deck over SSH, with the owner's authorization and no physical interaction. Visual rendering, controller, audio playback, live providers and in-game detection are still **NOT RUN**. Do not tick a row from source review, mock processes, DOM previews or Linux CI.

## Device and method

| Field | Recorded value |
|---|---|
| Operator | Claude Code (Claude Opus 5.5), remote SSH from the owner's Windows workstation; owner not present |
| Model | Steam Deck LCD (DMI product `Jupiter`) |
| SteamOS | 3.8.28, build 20260922.1, kernel 6.18.50-valve2-1-neptune-618, glibc 2.41 |
| Session / Steam | Gaming Mode (gamescope-session), Steam client stable channel |
| Gamescope | 3.16.23.6 (`gamescopectl` and `xprop` present) |
| Decky Loader | v3.2.10, PyInstaller bundle with embedded **CPython 3.11** (`libpython3.11.so.1.0`), developer mode on |
| Other plugins | Mako 4.5.0, Decky-Framegen 0.17, Decky LSFG-VK 0.14.4 (untouched) |
| espeak-ng | 1.52.0 (preinstalled) |
| Decky Pilot | ZIP from `d33edb7` (SHA256 `6e2aa460…`), then the build with this run's two fixes (SHA256 `c1638e65…`) |
| Plugin process | UID/GID 1000 (`deck`), not root (`flags: []`) |

Installation used the Loader's own local-ZIP path (`utilities/install_plugin` with a `file://` artifact, then `utilities/confirm_plugin_install`), which is what Developer → install from ZIP calls. The plugin backend was exercised through `loader/call_plugin_method` over an SSH tunnel to Decky's loopback port. Synthetic data only: two generated 1280×800 images with planted `SECRET` metadata markers, a fake `sk-ant-SYNTHETIC-NOT-A-REAL-KEY`, and an unreachable Ollama endpoint. No provider account, key or paid inference was used.

**Steam account safety constraints for every device run:** no game was launched, no Steam client file, setting, CEF debugger or account/Web API was touched, no input was injected into the Steam UI, and no screenshot was taken. Decky Pilot was the only plugin installed, upgraded or removed.

## Results

| Done | Test / measurable acceptance | Evidence |
|---|---|---|
| [x] | ZIP install/load/upgrade/uninstall; vendored Pillow ABI; reversible install; no leftover tasks | Install in 1.8 s, `Loaded DeckPilot (v0.1.0)`, no loader errors. Vendored cp311 Pillow loads under Decky's CPython 3.11. UPDATE install keeps `settings.json`/`secrets.json`/`chatgpt-auth.json` byte-identical (SHA256 compared). Uninstall removes the plugin directory, no process or user timer remains. Loader-created `data/` and `logs/` directories stay (Decky behavior). |
| [x] | Actual 0700/0600 ownership, no secret/content logs, consistent deletion/retention | Settings dir `0700`, all four JSON files `0600`, owner `deck`; `import-images` `0700`. The plugin log only has Loader lifecycle lines. The synthetic key appears only in `secrets.json`: never in RPC output, the plugin log or the Loader journal. `delete_local_data` removes all four files and restores defaults; imported originals are retained as documented. |
| [x] | Offline/denied provider/unreachable Ollama: safe errors/manual retry/no silent fallback | No provider → `NOT_CONFIGURED`. Missing consent → `CONSENT_REQUIRED`. Consented unreachable `127.0.0.1:11434` → `NETWORK_ERROR`, retryable, no fallback. Changing the endpoint revokes consent; `file://` endpoint and an interval under 90 s → `INVALID_INPUT`. |
| [x] | Manual image import: cleaned preview, path confinement (backend) | PNG and EXIF JPEG from the import folder → JPEG preview without the planted markers, 84–136 ms. `../settings.json` and a missing file are refused. Refused while images are disabled. The Decky picker UI itself is NOT RUN. |
| [x] | Capture stays unavailable until atomically safe targeting | `capabilities.capture=false`. `prepare_capture` returned misleading `CAPTURE_BLOCKED` ("paused, return to the game"); **fixed** to `CAPTURE_UNAVAILABLE` and re-verified on device, including the Steam UI app 769 context. See CAPTURE_VERIFICATION for the device environment finding. |
| [x] | ChatGPT loopback listener on device Python | `begin_chatgpt_sign_in` binds only `127.0.0.1` on an ephemeral port; a forged `state` and a wrong path get HTTP 400 and the state stays pending; cancel closes the listener with no leftover socket or hang on CPython 3.11. No request reached OpenAI and no browser was opened. |
| [x] | CPU/RAM idle | Idle plugin process: **0 CPU ticks in 60 s** (100 Hz clock), RSS about 82 MB, one thread. Frame rate, latency under load and sleep/resume are NOT RUN. |
| [~] | Local synthetic voice | espeak-ng 1.52.0 synthesizes `it`/`en` with the plugin's exact argv in about 20 ms per sentence, no playback. Its `--stdout` WAV has placeholder sizes (RIFF `0x7FFFF024`, data `0x7FFFF000`); **fixed** by rewriting the header to the real length. ffprobe accepts both forms (2.15 s); CEF playback, routing and Stop are NOT RUN. Nothing was played aloud. |
| [ ] | Real Decky rendering at 1280x800/720; readable text, scroll, no clipped controls | NOT RUN. Frontend import events were not delivered during this run (see platform findings); the panel loads on the next Steam or Deck restart. |
| [ ] | Controller/virtual keyboard, onboarding, focus after dropdowns/picker, Cancel and Stop reachable | NOT RUN (needs the owner at the device). |
| [ ] | Full English/Italian UI; independent UI/assistant languages retained across reload | Backend part verified: Italian safe errors, separate UI/answer languages kept across UPDATE. Visual UI NOT RUN. |
| [ ] | Steam/non-Steam/unknown/multiple-app detection; changes reject stale results | Backend: an `unknown` source pauses automation. Actual game detection NOT RUN: no game was launched, by the account-safety constraint. |
| [ ] | Six-second popup with QAM open/closed, full answer retained, dismiss on game change/unload | NOT RUN |
| [ ] | Speakers/headphones/Bluetooth, volume/routing/game audio, no residual playback | NOT RUN |
| [ ] | ChatGPT eligible account/workspace grant/denial, exact returned model labels, separate image eligibility, real refresh/revoke/limits | NOT RUN / account acceptance |
| [ ] | Steam system browser opens official authorization, callback returns to same backend device | NOT RUN (listener lifecycle above only) |
| [ ] | Native OpenAI/Claude/Gemini/xAI/Ollama text/image requests with dedicated authorized credentials | NOT RUN / provider acceptance |
| [ ] | Real ambiguous scene gives one useful question, player answer retained | NOT RUN / situation quality |
| [ ] | Once safe capture exists: session consent/indicator/pause, >=90 s, useful context only | Blocked by DP-016 |

## Decky Loader 3.2.10 platform findings

- **One websocket only.** The Loader keeps a single client socket, and a new connection closes the Steam frontend's. The frontend reconnects after about five seconds with a `FULL_SYNC` that drops the other client's pending replies. A test client must never resend a call, or the call runs twice; this caused a duplicated confirm/uninstall during this run, both harmless. Events emitted while the test client is connected (for example `loader/import_plugin`) do not reach the Steam UI.
- **SIGKILL on stop.** After a plugin has served at least one call, its event loop blocks inside the Loader's socket reader, so `_unload` cannot finish. The Loader then kills it five seconds after the stop request. The journal shows the same for Mako, Decky-Framegen and LSFG-VK since 22 September. Decky Pilot stays crash-consistent (atomic writes, nothing left running), but its cleanup code is not guaranteed to run on Deck.
- **No hot reload after an API install.** Rewriting `main.py` did not trigger a reload. Restarting Steam or the Deck loads the frontend.

Use sanitized synthetic evidence and reproducible issues for failures. Live API smoke is separate, optional and requires explicit consent and dedicated credentials.
