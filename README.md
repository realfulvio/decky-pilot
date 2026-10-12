# DeckPilot

Assistente italiano per Steam Deck dal menu Decky: chat, suggerimenti contestuali, immagini approvate e voce sintetica. MVP implementato e verificato offline; **pronto per validazione hardware, non certificato SteamOS**. La Steam Deck non era disponibile per questa consegna.

## Funzioni

- OpenAI Responses, Gemini generateContent, Claude Messages e Ollama chat attraverso REST reali nel backend Python. Nessun provider dimostrativo nel plugin.
- Contesto manuale: titolo, AppID facoltativo, obiettivo, posizione e note; funziona anche per emulatori. L'adapter Steam interno legge soltanto metadati quando la libreria e il contesto sono disponibili e non ambigui.
- Sessione nuova al cambio gioco, annullamento, una generazione globale, idempotenza locale e risultati obsoleti scartati.
- Popup da 6 secondi, testo breve e risposta completa nella chat. Soluzioni complete è il livello spoiler iniziale.
- Suggerimenti disattivati inizialmente: al massimo uno ogni 90 secondi, solo con contesto nuovo e recente. Pausa, deduplica, cooldown su errori e 20 tentativi automatici per sessione.
- PNG/JPEG scelti esplicitamente, con preview della versione ripulita/ridimensionata; consenso per ciascuna immagine e destinazione, handle monouso. Cattura diretta in Gaming Mode non disponibile.
- espeak-ng locale se già installato e OpenAI Speech remoto con consenso aggiuntivo. Un audio per volta; Stop e fallback testuale. Preferenza voce abilitata, disponibilità runtime rilevata.

Il solo titolo/AppID non rivela missioni o posizione. DeckPilot chiede dettagli quando mancano informazioni. Non controlla il gioco e non legge memoria, salvataggi o anti-cheat. Nessuna telemetria o server centrale DeckPilot.

## Primo avvio

1. Imposta il titolo e il contesto del gioco.
2. Nelle impostazioni scegli provider e un modello disponibile nel tuo account/server; non è predefinito alcun modello chat.
3. Inserisci e salva la chiave del provider cloud. Ollama non richiede chiave; `localhost` indica la Deck, non il PC di sviluppo.
4. Salva provider/modello/endpoint; il cambio destinazione revoca i consensi. Poi abilita e salva il consenso chat cloud o quello per lo specifico endpoint Ollama. Nessun test connessione viene avviato automaticamente.
5. Se desideri, premi «Verifica provider ora»: una verifica cloud esegue una breve generazione che può avere costi; Ollama usa `/api/show` senza download di modelli.
6. Immagini: conferma la capacità del modello, abilita import e scegli una singola immagine. Approva l'invio dopo aver visto preview, provider e modello. Per Ollama la capacità vision viene anche controllata via `/api/show`.
7. TTS OpenAI: scegli motore, modello e voce, salva le impostazioni e poi abilita/salva il consenso separato. Puoi usare «Salva chiave OpenAI per voce» anche con chat Gemini, Claude o Ollama. La chiave OpenAI serve sia alla chat OpenAI sia a Speech. I default Speech `gpt-4o-mini-tts`/`coral` sono documentati; la disponibilità sull'account resta da verificare.

L'abbonamento ChatGPT/Codex non prova disponibilità o credito API OpenAI. Nessuna chiave, cookie o token di Codex viene riusato. Non sono promessi prezzi o uso gratuito. HTTP su LAN espone contenuti alla rete: autorizza consapevolmente l'endpoint e preferisci HTTPS o un tunnel gestito da te. Questo progetto non configura VPN, SSH, firewall o servizi remoti.

## Immagini sul dispositivo

Il plugin usa il selettore ufficiale `openFilePicker` di Decky, ristretto a una cartella dedicata, indicata nella UI: `<DECKY_PLUGIN_RUNTIME_DIR>/import-images`. Copia qui soltanto immagini che vuoi analizzare. Il backend riceve il nome file, mai un path libero, e rifiuta traversal, symlink e file non immagine. L'originale importato è un file fornito dall'utente e rimane in questa cartella: elimina manualmente gli originali quando non servono. Le copie ripulite e i consensi restano in memoria per massimo 5 minuti e vengono consumati o revocati al cambio sessione/provider.

Il solo toggle non consente invii automatici. Nessun file viene letto prima di una scelta esplicita. Il selettore/controller in Gaming Mode è da verificare sul dispositivo; il browser harness usa upload di bytes per prove offline. JPEG/PNG: massimo 5 MiB, 20 MP, lato lungo 1280 px, payload ripulito fino a 1,5 MB. Nessun SVG o URL remoto.

## Sviluppo Windows

Toolchain verificata: Node 24.20.0, pnpm 10.28.2, Python 3.13 sul workstation. Target pacchetto: Loader ufficiale compilato con Python 3.11.7, Linux x86_64/glibc >= 2.28. Il pacchetto contiene Pillow CPython 3.11; altri ABI richiedono una build dedicata, non un'installazione pip nascosta sul dispositivo.

```powershell
corepack pnpm install --frozen-lockfile
py -3.13 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
corepack pnpm lint
corepack pnpm typecheck
corepack pnpm test
.venv\Scripts\python.exe -m ruff check backend main.py scripts tests/backend
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe scripts/scan_secrets.py
node scripts/audit.mjs
corepack pnpm build
.venv\Scripts\python.exe scripts/vendor.py
.venv\Scripts\python.exe scripts/package.py
```

Rollup usa la distribuzione ufficiale WebAssembly alla stessa versione per evitare dipendenze native bloccate dalla policy Windows. React e Decky UI sono esterni come nel template (`SP_REACT`, `SP_JSX`, `DFL`), senza seconda copia di React nella build.

## Linux e Cloud

```sh
corepack enable
pnpm install --frozen-lockfile
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
pnpm verify
.venv/bin/python -m ruff check backend main.py scripts tests/backend
.venv/bin/python -m pytest -q
.venv/bin/python scripts/scan_secrets.py
node scripts/audit.mjs
.venv/bin/python scripts/vendor.py
PYTHONPATH=vendor/py_modules .venv/bin/python -c 'from PIL import Image; print(Image.new("RGB", (1,1)).size)'
.venv/bin/python scripts/package.py
```

In Cloud collega il repository effettivo e rendi la specifica disponibile nel checkout. Non usare un nome repository come ID di ambiente. Il workflow include import della dipendenza Linux e permessi storage; non è stato eseguito su GitHub finché non esiste un remote autorizzato.

## Harness e verifiche

`corepack pnpm preview` apre un server solo su `127.0.0.1:5173`. Il banner «HARNESS OFFLINE» identifica risposte sintetiche e pulsanti di errore/attesa; non effettua chiamate API. `corepack pnpm exec playwright test` usa Microsoft Edge presente sul workstation e salva preview a 1280×800/720. Il test browser verifica focus da tastiera e flusso chat; non equivale a controller reale. Per Linux puoi impostare `PLAYWRIGHT_CHANNEL=chromium` e installare Chromium per Playwright.

I test backend bloccano DNS e il trasporto HTTP di produzione; i test protocollo usano trasporti iniettati. Nessuna API key reale è necessaria. Consulta [piano e risultati](docs/TEST_PLAN.md), [verifica API](docs/API_VERIFICATION.md) e [checklist hardware](docs/HARDWARE_VALIDATION.md).

## Pacchetto e installazione futura

`artifacts/deckpilot-0.1.0.zip` e `.zip.sha256` sono generati localmente; non sono una release pubblicata. La struttura contiene `DeckPilot/plugin.json`, `main.py`, `dist/index.js`, backend, documenti e `py_modules` con wheel/licenze. Nessuna venv, cache, chiave o file utente. `scripts/verify_package.py` verifica layout, checksum, manifest senza privilegi extra e ABI.

Sulla futura Deck, verifica versioni/ABI e abilita l'installazione ZIP dal menu sviluppatore Decky solo se desiderato; scegli lo ZIP locale secondo la UI del Loader installato. In alternativa copia reversibilmente la sola directory `DeckPilot` nel percorso plugin effettivo (spesso `~/homebrew/plugins`, da confermare sul target) usando le istruzioni del Loader. Nessuno script del progetto installa o modifica SteamOS.

Prima di disinstallare puoi cancellare tutti i dati dall'interfaccia. Unload ferma richieste, timer, processi audio e temporanei in memoria. Le impostazioni/chiavi possono essere mantenute dal Loader: elimina dati esplicitamente prima della rimozione. Gli originali nella cartella import rimangono file dell'utente e si eliminano manualmente. Nessuna directory esterna viene cancellata.

## Dati e troubleshooting

Chiavi: file privati in chiaro, directory 0700/file 0600 su Linux; non cifrati e non isolati da software locale compromesso. La UI restituisce solo stato configurato. Cronologia in memoria; opzionalmente su disco, 100 messaggi/gioco per 7 giorni, max 20 giochi/1,8 MB globali (evizione locale). Cancellazione cronologia non cancella chiavi; cancellazione globale cancella configurazione, chiavi e cronologia, non copie già inviate ai provider o originali importati. Le diagnostiche sono sanitizzate e vanno riviste prima di condividerle.

- Provider non configurato: salva modello/chiave, poi consenso; nessun fallback remoto implicito.
- Immagine non supportata: verifica la capacità e il modello, rimuovi esplicitamente l'allegato se vuoi proseguire solo col testo.
- Voce non disponibile: testo sempre accessibile; espeak-ng non viene installato automaticamente. Verifica separatamente consenso e chiave OpenAI per Speech.
- Rete/rate limit: riprova manualmente dopo l'attesa; nessun retry automatico pagato. Annullare non garantisce che il provider annulli o rimborsi il lavoro.
- Archivio corrotto/ownership errata: il caricamento fallisce senza azzerare dati. Conserva una copia locale sicura e ripara permessi/schema; non allegare `secrets.json` ai bug report.

[Privacy](docs/PRIVACY.md), [sicurezza e audit](docs/SECURITY.md), [architettura](docs/ARCHITECTURE.md), [backlog](docs/BACKLOG.md), [handoff](docs/CODEX_HANDOFF.md).

Licenza BSD-3-Clause; attribuzione al template Steam Deck Homebrew e licenze delle dipendenze in [THIRD_PARTY_NOTICES.md](docs/THIRD_PARTY_NOTICES.md) e nella wheel Pillow inclusa.
