# Implement DeckPilot MVP with secure providers, contextual hints and TTS

Il checkout disponibile non aveva DeckPilot. Questa PR introduce un plugin Decky compilabile con UI italiana, backend validato e REST reali OpenAI Responses,Gemini,Claude e Ollama. La chat usa contesto esplicito e chiede dettagli se il gameplay non è noto.

Implementati settings/chiavi private,consensi chat/endpoint/immagini/Speech,sessioni/cancel,hint server minimo90s e contesto nuovo,popup6s/crono completa,importPNG/JPEG ripulito/preview/consenso monouso,TTS espeak-ng rilevato/Speech remoto con Stop/fallback. Nessun mock produzione,telemetria,capture implicita o fallback remoto non autorizzato.

Verifica:116 test Python passati(2 symlink skip Windows),11 frontend,2 browser1280×800/720,Ruff/ESLint/TypeScript/buildWASM,contratti,scan,wheel LinuxCP311 hash-pinned e package/checksum. Workflow read-only con ActionsSHA predisposto; risultato remoto da osservare.

Audit: Rollup del template corretto;1 eccezione braces build-only senza patch upstream,documentata/shown dal check. Non inclusa nel runtime.

## Non ancora verificato su Steam Deck

- Installazione/backend/PythonABI Linux/UID/ownership/POSIX.
- Controller/tastiera/focus,rendering Decky,popup QAM chiuso.
- Steam interno,picker reale,IPC/audio/TTS e routing.
- CPU/RAM/frame rate/sleep-resume. Checklist NON ESEGUITA.
- Capture diretta unavailable; import manuale implementato e backlog dedicato.

Nessuna API privata/live smoke,installazione dispositivi,store/release/merge. MVP per revisione/validazione hardware,non dichiarato production-ready.
