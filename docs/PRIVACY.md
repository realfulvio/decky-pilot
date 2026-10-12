# Privacy and data control

No telemetry and no Decky Pilot central server. Defaults: no provider, no remote/endpoint consent, no images or capture, no automatic assistance, no persistent history. Voice preference requires an available engine and the relevant consent. Interface and assistant languages initially default to English.

| Path | Shared data | Permission / revocation | Local retention |
|---|---|---|---|
| Cloud chat | Supplied title/AppID/objective/area/notes, selected recent messages and question | Selected provider/model and chat consent; recipient change revokes consent | Session memory; optional limited persistence |
| Ollama | Same data at the authorized address | Separate endpoint consent; HTTP warning | Server may forward to cloud; do not assume local-only processing |
| Manual image | Only the cleaned JPEG shown in preview | Images enabled, explicit selection, per-image recipient/session approval | One-use copy, five-minute expiry; original import remains user's file |
| Direct capture | None in this build | Safety gate closed; no account/key screen acquisition | No production screenshot acquisition |
| Automatic visual path | Gameplay copy plus current context, if eventually enabled | Separate per-session acquisition/send consent, visible state and immediate pause | Bounded temporary copy; no image history; currently unavailable |
| OpenAI Speech | Up to 1,000 characters of the answer and pronunciation instructions | Separate Speech consent/OpenAI key, even with a different chat provider | WAV memory until completion/Stop |
| Local espeak-ng | Answer on process stdin | Voice preference and existing engine | WAV memory; no networking |

Do not import keys, sign-in screens or account details. Image cleaning removes metadata, not private content visible in pixels. The plugin does not certify automatic redaction. Automatic acquisition stays disabled because inspected Gamescope sources cannot guarantee a game-only target during focus changes. [Capture findings](CAPTURE_VERIFICATION.md).

SteamID, friends, profile, library, hostname, local paths and machine telemetry are not sent in prompts. AppID does not reveal gameplay. UI and assistant languages are independent; the assistant language controls responses and speech. Voice reads existing text without translating old history.

Keys are plaintext private files in the official Decky settings directory (0700/0600 POSIX), never returned through RPC or stored in browser storage. A saved key is not proof of validity. Key deletion cancels work and revokes image/session approval; compromised software with local access can still read files/process memory. No keyring/encryption is claimed.

History defaults to session memory. Opt-in persistence retains at most 100 messages/game, seven days, 20 games/1.8 MB total with eviction and periodic expiry. Clear conversation deletes that game's disk/memory history and pending voice/images while keeping keys. Delete local data removes keys/config/history and cancels work; original files you copied into the import folder remain and must be removed manually if desired. Loader uninstall can retain settings: delete explicitly before removal.

Local deletion does not erase already sent provider data; cancellation does not guarantee remote cancellation or refunds. OpenAI `store:false` does not mean zero retention. Terms depend on account/plan: consult [OpenAI data controls](https://developers.openai.com/api/docs/guides/your-data), [Gemini terms](https://ai.google.dev/gemini-api/terms), [Claude privacy](https://privacy.claude.com/) and your chosen Ollama server policy. No uniform free-use or data-training promise is made.

Sanitized status contains capabilities/configuration/limits, not prompts, keys, audio, screenshots, answer content or remote tracebacks. Diagnostics are kept out of the normal UI. Review any evidence before sharing; fixtures and preview samples are synthetic.
