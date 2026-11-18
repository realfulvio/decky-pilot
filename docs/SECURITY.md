# Security

Decky plugins share a local environment. Manifest flags are empty; inspected Loader code uses the host user, but actual Deck UID/ownership remains unmeasured. No strong sandbox, encryption or protection from compromised local software is claimed.

| Threat | Implemented control | Limit |
|---|---|---|
| Key/log leakage | Separate backend secrets, public configured booleans, safe localized error codes, no remote bodies/logged contents, cleared key inputs | Plaintext local files/process memory remain accessible to their user |
| OAuth substitution/replay | Own temporary loopback, state/nonce/PKCE, issued client, signed JWT/JWKS issuer/audience/expiry/sub checks; validate before active account replacement | Real account/device eligibility NOT RUN; one backend instance per credential directory |
| Expired plan or incompatible vision | Serialized refresh/revoke, selected-account catalog, independent image gate and usage-limit pause | Remote revocation can fail; local clearing cannot retract sent data; no paid/provider fallback |
| RPC/consent manipulation | Backend method/field allowlists, type/range checks, authoritative settings; chat cannot choose recipient | Same-user plugins are not separate trusted sandboxes |
| Path/symlink abuse | Byte upload; basename-only dedicated image root; owner/parent/symlink checks and POSIX O_NOFOLLOW | No protection promised against all same-UID filesystem races |
| SSRF/DNS/redirect | Fixed HTTPS cloud hosts, explicitly authorized Ollama host, all addresses validated and pinned, metadata/link-local/CGNAT/translation blocked; no redirect/proxy | LAN/loopback allowed intentionally; no firewall/tunnel setup |
| Unwanted screen capture | Production safety gate closed; no screenshot command executed; no account/key screen scanning | Manual users must remove sensitive image content themselves |
| Costs/flood | One generation, idempotence, bounded deadlines/output, 90-second automatic cooldown, useful fresh context, per-session consent, pause, error limit and 20-attempt budget | No hard monetary limit; work already sent can still be billed |
| Prompt injection | Trusted policy separate from untrusted context/images; no tools/shell/retrieval | Models can be wrong or violate spoiler instructions |
| Image bombs | Real static PNG/JPEG decode, 5 MiB/20 MP limits, resize/re-encode and metadata removal | Native Pillow ABI and updates still matter |
| Shell/audio | Fixed subprocess argv/stdin, bounded stdout, timeout/Stop and object URL revocation | Hardware routing/quality unverified |
| Supply chain | Exact versions/lockfile, wheel hash, Actions commit pins, read-only CI, secret scan and audit | Hashes do not eliminate upstream compromise |

## Dependency audit: 12 October 2026

Template Rollup 4.53.3 was replaced with official Rollup WASM 4.64.5 for every resolution, fixing [GHSA-mw96-cpmx-2vgc](https://github.com/rollup/rollup/security/advisories/GHSA-mw96-cpmx-2vgc). WASM also avoids the native module blocked by this Windows workstation's policy, without changing that policy.

The previously allowed high [GHSA-vfj7-8cjw-p6xm](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm) affects `braces <=3.0.3`; no patched release was found at review. Chain: `@decky/rollup > rollup-plugin-delete > del > globby > fast-glob > micromatch > braces`. Updating the delete plugin alone retains that chain.

**Resolved by removing the vulnerable chain**, not hiding it: local Rollup config adapts the official npm preset 1.0.2, preserving its transformation plugin versions, external globals, assets and output. Direct dependencies replace the preset. Node's built-in cleanup deletes only the project's absolute `dist` directory, rejecting files, symlinks and junctions. No glob/delete dependency or fake braces replacement remains in the lockfile. BSD attribution is preserved.

In security commit `cefedad`, the before/after JS bundle was byte-identical: SHA256 `103b977544f3d50ee12a461e023f19f20c7fb4e526b44cf27f12bd80be9dd951`. Subsequent UI work intentionally changes the bundle. Registry audit reported zero advisories with this lockfile; this is dated evidence, not a guarantee about unknown vulnerabilities.

The exception was removed. `scripts/audit.mjs` displays all advisories and fails on every high/critical, including the formerly allowed ID. Missing, interrupted, invalid or incomplete registry reports also fail. Tooling tests cover these failures and confined cleanup. No audit, secret scan or CI control is disabled. Deprecation notices are distinguished from advisories.

## Storage, cleanup and reporting

POSIX directories 0700/files 0600, owner checks and temporary/fsync/replace writes; invalid/corrupt/future storage fails without reset. Windows does not prove Linux permission behavior; Linux CI runs these checks, while Deck ownership is deferred. Unload and context/consent changes stop tasks/processes/image handles/audio. Remote work and OS DNS cancellation are best effort.

Secret scanning suppresses matching contents and checks common key/PEM formats; it cannot prove the absence of every secret. ZIP verification rejects private/development paths. No real provider credentials were used. Report security categories and reproducible steps with synthetic data; never publish keys, account screens or private gameplay.
