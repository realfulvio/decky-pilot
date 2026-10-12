# Validazione Steam Deck differita

Stato: **NON ESEGUITA — Steam Deck non disponibile**. Nessuna installazione su dispositivi/mini PC. Test offline e API non certificano Gaming Mode.

| Campo target | Valore |
|---|---|
| Data/esecutore, modello LCD/OLED | NON ESEGUITA |
| SteamOS/kernel/glibc | NON ESEGUITA |
| Steam client/canale, Decky/versione/commit | NON ESEGUITA |
| Python runtime/ABI | NON ESEGUITA |
| DeckPilot commit/ZIP checksum | NON ESEGUITA |
| UID/GID/ownership settings/runtime | NON ESEGUITA |
| espeak-ng/versione, provider/modello/Ollama | NON ESEGUITA (mai annotare chiavi) |

| Eseguito | Prova e criterio verificabile | Evidenza/risultato/issue |
|---|---|---|
| [ ] | Installazione ZIP/caricamento/upgrade/uninstall: backend/Pillow CP311, reversibilità, no task residui, retention coerente | NON ESEGUITA /DP-015 |
| [ ] | Controller/tastiera virtuale/focus dopo dialoghi, scroll chat e Cancel/Stop accessibili | NON ESEGUITA /DP-015 |
| [ ] | Layout1280×800/720 con gioco: testo leggibile, no overflow/focus sottratto, UI produzione Decky | NON ESEGUITA /DP-015 |
| [ ] | Steam cambio titolo/non Steam/undefined/più app: fallback, unknown sospende auto, no risultati precedenti | NON ESEGUITA /DP-015 |
| [ ] | Popup circa6s misurati con QAM chiuso/aperto, risposta completa, dismiss su cambio/unload | NON ESEGUITA /DP-015 |
| [ ] | Auto minimo90s, sleep/resume/reload senza raffiche, no solo titolo, pause/errori/budget | NON ESEGUITA /DP-015 |
| [ ] | Picker ristretto/preview effettiva/approvazione/destinatario/revoca, niente lettura automatica | NON ESEGUITA /DP-015 |
| [ ] | Capture Gaming Mode resta unavailable; futura soluzione con capability/consensi/test separati | NON ESEGUITA /DP-016 |
| [ ] | TTS locale/remoto: disclosure voce sintetica, motore assente→testo, IPC audio/cancel/stop | NON ESEGUITA /DP-015 |
| [ ] | Altoparlanti/cuffie/Bluetooth, volume/routing/interferenza audio gioco, no voce residua | NON ESEGUITA /DP-015 |
| [ ] | Offline/provider negato/rate limit/Ollama irraggiungibile: errori sicuri/retry esplicito/no fallback | NON ESEGUITA /DP-015 |
| [ ] | Storage0700/0600 owner reale, log senza segreti/contenuti, cancellazione coerente | NON ESEGUITA /DP-015 |
| [ ] | Misure CPU/RAM idle/latenza/frame rate/sleep-resume: riportare strumenti/metodo e dati reali | NON ESEGUITA /DP-017 |

Registra evidenze sanitizzate e issue riproducibili per i fallimenti. Non pubblicare chiavi/account/gameplay privato. Nessuna spunta hardware dai mock/DOM/build. M4 richiede evidenze e correzioni prima di dichiarare compatibilità reale.
