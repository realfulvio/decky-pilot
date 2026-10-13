# Claude Code — handoff frontend e percorso manuale immagini (13 ottobre 2026)

Documento di Claude Code, separato dall'handoff canonico gestito da Grok
([HANDOFF-2026-10-13.md](../HANDOFF-2026-10-13.md), non modificato).

- Branch: `claude/decky-pilot-frontend-20261013`, base `19de507`
  (`origin/codex/decky-pilot-safe-capture-20261013`, che al momento coincideva col checkpoint noto).
- Worktree: `~/work/decky-pilot-claude` (notebook). Checkout condiviso non toccato.
- Commit di correzione: `eda133c` più questo documento.
- Ambito: solo frontend, harness offline e test. Backend, gate di cattura e sessione grafica
  del mini-PC **non** toccati. `CAPTURE_SAFETY_VALIDATED = False` invariato.

**Natura delle prove:** vitest/jsdom e Playwright Chromium headless sul harness offline con
backend simulato (`FakeBridge`). **Non** sono una verifica nel menu Decky reale né su Deck/mini-PC:
i passi UI 1-5 dell'handoff canonico restano da eseguire sul dispositivo.

## Problema riprodotto e corretto

Percorso dell'handoff (provider "nessuno", solo "Consenti immagini del gioco", import del PNG
sintetico). Il backend (`Service.destination()`) restituisce `provider: null, model: ""`. La scheda
di revisione mostrava letteralmente **`Share with {provider} · `** (`Condividi con {provider} · `),
perché `translate` lascia il segnaposto quando il valore è `null`, e il pulsante
"Consenti l'invio di questa immagine" restava attivo senza alcun destinatario. Riprodotto in
vitest prima della correzione (3 nuove regressioni falliscono sul codice originale, passano dopo).

Correzione (`src/components/App.tsx`, `src/domain/types.ts`, `locales/*.json`):

- Destinatario con nome leggibile (`OpenAI`, `ChatGPT`, `Claude`…) e modello salvato.
- Senza servizio/modello: nuovo testo `imageNoRecipient` ("l'immagine resta sul dispositivo…")
  e approvazione per immagine disabilitata. "Aiutami ora"/"Chiedi" restano disabilitati.
- Dopo l'approvazione: riga `role="status"` `imageApproved` con destinatario. Il pulsante di
  approvazione resta al suo posto (scelta voluta: non far perdere il focus del controller).
- Il tipo `PreparedImage.destination.provider` ora ammette `null`, come il backend reale.
- Due chiavi aggiunte a `locales/en.json` e `it.json` (catalogo condiviso col backend: parità
  chiavi verificata dai test frontend e da `test_localization_capture.py`).

Harness (`src/harness/fakeBridge.ts`, mai importato da `src/index.tsx`): supporta
`prepare_import_image` (percorso del picker Decky) con PNG sintetico 1×1 e replica i controlli del
backend: sessione corrente, `imagesEnabled`, destinazione dalle impostazioni salvate
(`endpoint: 'cloud'` o endpoint Ollama), verifica destinazione su `approve_image_send`.

## Verifiche del percorso manuale (backend simulato)

| Passo | Esito |
| --- | --- |
| Salvataggio gioco `Test` / `prova` | `set_game_context` inviato, titolo mostrato in Gioca |
| Impostazioni senza provider/chiavi | select su "Scegli un servizio", nessuna chiave salvata, nessun `set_api_key`/`list_models` |
| Consenso immagini distinto dall'invio | attivando solo immagini: `remoteConsent`/`endpointConsent` restano `false` dopo il salvataggio |
| Import PNG sintetico (picker Decky) | `prepare_import_image` con `{filename, sessionId}` esatti |
| Import PNG sintetico (input file browser) | anteprima visibile in Chromium 360×720, nessun overflow orizzontale |
| Anteprima e destinatario | senza servizio: avviso "nessun destinatario"; con OpenAI: "Share with OpenAI · sample" |
| Rimozione | `discard_image` con il riferimento; anteprima rimossa; attivabile da tastiera (focus + Invio) |
| Nessun invio | nessun `approve_image_send`, `start_assistant_request`, `prepare_capture`, `test_provider` |
| Stati disabilitati | import disabilitato senza consenso immagini salvato e senza gioco |
| Errori | errore del picker (es. fuori cartella import) → avviso `role="alert"`, nessuna preparazione |
| Italiano | avviso localizzato, pulsante "Consenti l'invio…" disabilitato |

Comandi (Node 24.20.0 locale in `artifacts/toolchain`, Node globale 26 non toccato;
Chromium Playwright in `artifacts/playwright`; venv Python 3.14.8 in `artifacts/venv`):

| Controllo | Esito |
| --- | --- |
| `corepack pnpm verify` (ESLint, tsc, vitest, tooling, build Rollup) | verde; vitest **32** (27 + 5 nuovi), tooling 13 |
| `PLAYWRIGHT_CHANNEL=chromium corepack pnpm exec playwright test` | **7** passati (6 + 1 nuovo) |
| `pytest tests/backend` (backend non modificato, locale aggiornati) | **213** passati con `--basetemp artifacts/p` |
| `ruff check backend main.py scripts tests/backend` | pulito |
| `scripts/scan_secrets.py`, `git diff --check` | passati |

Nota ambientale: con un `--basetemp` lungo, 11 test della sonda Wayland falliscono con
`OSError: AF_UNIX path too long` (limite 108 byte del socket Unix), non per un difetto. Con un
percorso corto passano tutti.

## Osservazioni non corrette (nessun difetto dimostrato o fuori ambito)

- Con servizio "nessuno" le Impostazioni mostrano comunque il campo "Chiave API" (salvataggio
  disabilitato). Confonde ma non salva nulla; lasciato invariato.
- Su Decky `pickImage` restituisce `null` in silenzio se `importRoot` manca. Il backend lo espone
  sempre, quindi non è stato riprodotto un caso reale.
- L'anteprima di un PNG 1×1 è quasi invisibile: è un limite del dato sintetico, non della UI.
- Focus/D-pad reali (`Focusable`, `ButtonItem`, `ToggleField` di `@decky/ui`) non sono verificabili
  nel harness: servono i passi UI 1-5 sul mini-PC o sulla Deck.

Invariati: popup 6000 ms, voce, spoiler, provider, opzioni esistenti, cattura automatica
disabilitata, nessuna richiesta AI reale, nessun sudo/pacchetto/rete/autostart/merge/release.

## Prossimo passo

Su dispositivo (Grok, sessione grafica del mini-PC): rifare i passi UI 1-5 con questo frontend
(ricostruire lo ZIP dal branch) e verificare che la scheda dica "Nessun servizio AI scelto…"
invece di `Condividi con {provider}`, con approvazione disabilitata e rimozione funzionante.
