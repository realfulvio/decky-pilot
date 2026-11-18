# SteamOS / Gamescope capture verification

Reviewed 12 October 2026 against official [ValveSoftware/gamescope](https://github.com/ValveSoftware/gamescope/tree/1b17fcc1b6ba4b657d39cf374d287191e40476b0), commit `1b17fcc1b6ba4b657d39cf374d287191e40476b0`. This is source verification, not a Steam Deck test. No software was installed on a device.

## Actual mechanism

The official [gamescopectl CLI](https://github.com/ValveSoftware/gamescope/blob/1b17fcc1b6ba4b657d39cf374d287191e40476b0/src/Apps/gamescopectl.cpp) connects to the Gamescope private Wayland control socket using `GAMESCOPE_WAYLAND_DISPLAY`, default `gamescope-0`. Its command path invokes concommands. `gamescopectl screenshot <path>` is backed by the [screenshot concommand](https://github.com/ValveSoftware/gamescope/blob/1b17fcc1b6ba4b657d39cf374d287191e40476b0/src/steamcompmgr.cpp), which accepts a destination and defaults to base-plane-only output. The base-plane screenshot path strips overlay layers and encodes asynchronously, so CLI exit is not evidence that the image has finished writing.

The [control protocol](https://github.com/ValveSoftware/gamescope/blob/1b17fcc1b6ba4b657d39cf374d287191e40476b0/protocol/gamescope-control.xml) has `take_screenshot` since version 3, with path/type/flags and a completion event. It is explicitly private, not an API for arbitrary Wayland clients. Neither this request nor the CLI screenshot command accepts a target app/window ID. Focus properties `GAMESCOPE_FOCUSED_APP` and `_GFX` identify current input/graphics focus, not an atomic screenshot binding. The older shared `/tmp/gamescope.png` X11 trigger was rejected because of its shared output and targeting limitations.

## Implemented but disabled

`backend/capture.py` implements the real fixed-argument CLI path, only with an existing executable and local owned Gamescope socket, local X display and matching confirmed Steam app/input/graphics focus. It excludes Steam app 769, unknown/manual context, remote displays, symlinks and arbitrary RPC output paths. It uses a unique private directory, bounded process/output/image sizes, waits for actual PNG verification, checks focus again and cleans up on success/error/cancellation. It does not read a framebuffer, install tools, use a shell or require root.

**These checks cannot guarantee that an account or key surface was never acquired between focus checks.** This is an inference from the upstream request's missing target binding and asynchronous global focus selection. User confirmation and pre/post checks alone do not close that race. Therefore `CAPTURE_SAFETY_VALIDATED=False` and `capabilities.capture=false` in production. No screenshot command is run by manual or automatic production paths; manual import remains available. `prepare_capture` fails clearly with CAPTURE_UNAVAILABLE. Test doubles exercise synthetic pixels and lifecycle only; they never enable production capture.

The UI and backend have explicit-action preview/approval and separate per-session automatic consent, visible status and pause. These paths are implemented but unavailable pending a safe capture mechanism. Automatic attempts require fresh useful context, at least 90 seconds, deduplication and budget/error controls; no continuous screenshot polling is provided.

## Steam Deck observations, 17 October 2026

Read-only checks on SteamOS 3.8.28 with Gamescope 3.16.23.6; no screenshot was taken.

- `gamescopectl` and `xprop` are installed. With `XDG_RUNTIME_DIR=/run/user/1000`, `gamescopectl help` lists `screenshot`; the `gamescope-0` socket is owned by `deck`, mode 0755.
- In the Steam UI, `GAMESCOPE_FOCUSED_APP` and `_GFX` on `:0` are both `769`, the ID the adapter already excludes; `:1` has no focus properties.
- **Decky plugins do not inherit the session environment.** The Loader is a root system service whose unit sets only `UNPRIVILEGED_PATH`, `PRIVILEGED_PATH` and `LOG_LEVEL`. Its sandbox adds `HOME`, `USER` and `DECKY_*`, with no `DISPLAY`, `XDG_RUNTIME_DIR` or `GAMESCOPE_WAYLAND_DISPLAY`. So `GameCapture.probe()` returns false at its first environment check even before `CAPTURE_SAFETY_VALIDATED`, and `gamescopectl` fails without `XDG_RUNTIME_DIR`. A future adapter would have to supply a verified session environment explicitly; values from `/run/user/1000/gamescope-environment` must be validated, not trusted.
- `prepare_capture` used to answer `CAPTURE_BLOCKED` ("paused, return to the game"), which suggested capture would work later. It now checks availability first and answers `CAPTURE_UNAVAILABLE`, verified on the device.

## Criteria before enabling acquisition

1. Find or implement an audited compositor-side mechanism that atomically binds acquisition to the confirmed game's surface/frame and refuses Steam/QAM/sign-in/account/other surfaces. A system screenshot helper without targeting is insufficient. Determine required privileges, package availability, licenses and version support.
2. Verify the actual SteamOS/Gamescope version, socket, installed CLI, Decky UID/runtime and ABI. Do not claim upstream master is the shipped SteamOS version.
3. Demonstrate sensitive-screen refusal before acquisition under rapid focus changes, settings/key entry, sign-in, Steam/QAM overlays, game exit/switch, non-Steam games, multiple apps and sleep/resume. Instrument with synthetic privacy test screens; do not capture real secrets.
4. Check completion, timeout, PNG bounds, cancellation, cleanup, no stale images, per-image recipient approval and consent revocation.
5. Measure latency/load and validate explicit and automatic modes on hardware, including controller focus, visible active state, immediate pause, 90-second minimum and useful-context suppression.

Only after a reviewed solution and evidence satisfy these requirements should the gate change in a dedicated commit. The build is reviewable without hardware; direct capture and automatic visual help must not be described as working on Steam Deck meanwhile.
