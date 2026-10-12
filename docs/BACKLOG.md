# Backlog

Chiuso = implementato/verificato offline, non certificato hardware. Nessuna issue remota creata; backlog pronto per il repository.

| ID/priorità | Titolo/contesto | Stato/riferimenti | Acceptance/dependenze |
|---|---|---|---|
| DP-001 P0 | Bootstrap/verifica ufficiale | CHIUSO locale: API_VERIFICATION,package/lockfile,rollup | Build/import passano,fonti/versioni/commit registrati; CI remota gate distinto |
| DP-002 P0 | RPC/contratto condiviso | CHIUSO: service.rpc,contracts,test_contract_lifecycle/frontend | Allowlist/range,errori sicuri,stesso schema Python/TS,dominio senza Decky. Dip001 |
| DP-003 P0 | Settings/API keys | CHIUSO offline: storage.py,test_storage | Atomicità,delete,no valori pubblici,corruzione preservata; POSIX/symlink da Linux/015. Dip002 |
| DP-004 P0 | OpenAI Responses/vision | CHIUSO: providers.OpenAI,test_providers | Input/image native,Bearer/storefalse,blocchi/usage/errori. Dip003 |
| DP-005 P0 | Gemini nativo | CHIUSO: providers.Gemini,test_providers | Parts/inlineData/header,blocchi/empty/thought filtrato,usage/errori. Dip003 |
| DP-006 P0 | Claude Messages/vision | CHIUSO: providers.Claude,test_providers | System/auth/versione,base64,no thinking; workspace singolo documentato. Dip003 |
| DP-007 P0 | Ollama/rete/capacità | CHIUSO: providers.Ollama/transport,test_urls/test_transport_import | Endpoint autorizzato,/show,chat,DNS pinning/SSRF/redirect. Dip003 |
| DP-008 P0 | Sessioni/contesto/Steam isolato | CHIUSO offline: context/service/gameContextAdapter,tests | Manuale senzaAppID,no stale,shape/undefined/ambiguità/fallback; Steam reale da015. Dip002 |
| DP-009 P0 | Scheduler | CHIUSO: service.tick,test_service |0/89/90,lock,no raffica resume,contesto nuovo,pause/dedup/errori/budget. Dip008 |
| DP-010 P0 | Popup6s/crono completa | CHIUSO offline: popupPresenter/controller,frontend | Duration6000,no suono,limiti,dismiss,risposta intera; visibilità reale da015. Dip008 |
| DP-011 P0 | Immagini opt-in reali | CHIUSO offline: images/prepare_import_image/Chat,tests | JPEG/PNG ripuliti,preview,consenso monouso,no path libero; picker reale da015. Dip004–008 |
| DP-012 P0 | TTS locale/remoto/stop | CHIUSO offline: tts/audioPresenter,tests | Speech reale,stdin sicuro,runtime detection,secondo consenso,cleanup; audio reale da015. Dip008 |
| DP-013 P0 | Test/CI/package | CHIUSO locale: scripts/workflow/tests | Offline/build/ZIP verificati,CI scritta ma non osservata senza remote. Dip001–012 |
| DP-014 P0 | Privacy/security/delete | CHIUSO: PRIVACY/SECURITY,service,tests | Default/consensi/retention/errori/delete; review braces al gateM4. Dip003/011/012 |
| DP-015 P1 | Hardware/compatibilità Linux | APERTO: HARDWARE_VALIDATION | Versioni/ABI/UID/install/controller/picker/popup/audio/IPC/permessi con evidenze,correggere fallimenti. Dip013/014 |
| DP-016 P1 | Capture Gaming Mode | APERTO; capabilityfalse/import reale | Metodo circoscritto verificato,licenze/privilegi,consenso ogni capture/invio,fallback/test. Dip015 |
| DP-017 P1 | Performance/sleep/resume | APERTO | Misurare CPU/RAM/latenza/frame rate/wakeup,no raffiche/worker doppi,metodo/valori reali. Dip015 |
| DP-018 P2 | Streaming reale | APERTO | Parser nativi/backpressure/cancel,contratti testati,no token finti. Dip004–007/015 |
| DP-019 P2 | Shortcut controller | APERTO | Mapping verificato,toggle esplicito,no input rubato,controller reale. Dip015 |
| DP-020 P2 | STT/OCR/retrieval/profili | APERTO | Proposte separate,consensi/limiti/fonti e test dedicati,no attivazione implicita. Dip014/015 |

Gate esterno aperto: repository remoto corretto, push e PR senza merge. Remote/proprietario non inventati; nessun nuovo repository GitHub creato senza destinazione fornita.
