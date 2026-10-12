# DeckPilot

Assistente di gioco per Decky che aiuta a trovare il prossimo passo. L'inglese è predefinito; la traduzione italiana completa si sceglie nelle Impostazioni. [Read in English](README.md).

MVP in revisione nella [PR #1](https://github.com/realfulvio/decky-pilot/pull/1). La [galleria nella PR #2](https://github.com/realfulvio/decky-pilot/pull/2) mostra le stesse schermate React in un'anteprima offline dichiarata. La Steam Deck non è disponibile: la compatibilità hardware rimane da verificare.

## Chiedere aiuto

1. Segui **Inizia**: scegli il gioco, collega un servizio AI e decidi cosa condividere. La configurazione non invia richieste AI.
2. In **Gioca**, usa **Aiutami ora** o scrivi una domanda. L'ultima risposta e i controlli voce sono insieme.
3. Per assistenza visiva, abilita le immagini nelle Impostazioni, scegli un PNG o JPEG contenente soltanto il gioco, controlla anteprima e destinatario e approva quella singola immagine prima di inviarla. Su Deck, copia il file nella cartella import dedicata indicata nelle Opzioni avanzate e scegli con il selettore Decky.

OpenAI, Claude e Gemini usano le API multimodali native reali; Ollama usa chat nativa e controlla le capacità del modello. Scegli un modello disponibile nel tuo account e confermane il supporto immagini. Nessun modello viene sostituito implicitamente e nessun provider cambia senza scelta e nuovo consenso. Le API possono costare; l'abbonamento ChatGPT non include credito API.

Uno screenshot può suggerire area e obiettivo, ma non ricostruisce progressi, inventario o missioni nascoste. I prompt chiedono di distinguere osservazioni e ipotesi, proponendo un passo concreto o una domanda se manca contesto. Accuratezza e rispetto degli spoiler non sono garantiti.

## Cattura e assistenza automatica

**La cattura diretta in Gaming Mode non è disponibile in questa build.** Abbiamo verificato il comando screenshot reale di Gamescope e implementato un adapter limitato, ma l'acquisizione resta disabilitata: il comando upstream non lega atomicamente l'immagine alla finestra del gioco e può acquisire un'altra superficie durante il cambio di focus. Non soddisfa l'esclusione delle schermate di chiavi e account. Nessuna cattura simulata in produzione o API Steam inventata. [Riscontri e criteri di accettazione](docs/CAPTURE_VERIFICATION.md).

Importazione e analisi manuali sono implementate. Aiutami ora offre l'importazione se le immagini sono abilitate, altrimenti usa il contesto fornito.

Il percorso automatico visivo opzionale è implementato e testato offline, ma non disponibile finché la cattura è disabilitata. Richiede consenso separato per la sessione corrente, indicatore visibile, pausa immediata e almeno 90 secondi fra tentativi. Serve contesto nuovo e utile; contesti/immagini identici, gioco sconosciuto, richieste/voce attive, errori e sleep/resume impediscono lavoro. Non scansiona continuamente lo schermo e non deduce che sei bloccato. Cambio gioco, reload, impostazioni o chiavi revocano il consenso. Dopo 20 tentativi serve una nuova autorizzazione. Nessun test hardware dichiarato.

## Lingue e voce

Tre scelte indipendenti: lingua interfaccia, risposte AI e voce. Tutte iniziano in inglese; ciascuna supporta inglese e italiano. Cataloghi condivisi coprono interfaccia, errori sicuri e prompt. I nuovi default preservano impostazioni valide e chiavi esistenti.

La voce legge il testo già scritto con la pronuncia scelta: non traduce la risposta. Locale: espeak-ng soltanto se già installato. Online: OpenAI Speech con chiave/consenso separati e gpt-4o-mini-tts, che supporta istruzioni di pronuncia indipendenti. Voce sintetica dichiarata; il testo rimane se l'audio fallisce. Nessuna installazione automatica di espeak-ng.

## Sviluppo e verifiche

Versioni fissate: Node 24.20.0, Corepack/pnpm 10.28.2, Python 3.11.7 nella CI Linux; sviluppo Windows Python 3.13.15. Produzione: Decky API 1.1.3 e UI 4.12.1, React/UI esterne al bundle.

```sh
corepack pnpm install --frozen-lockfile
python -m venv .venv
# Attiva la venv nella tua shell, poi:
python -m pip install -r requirements-dev.txt
corepack pnpm verify
python -m ruff check backend main.py scripts tests/backend
python -m pytest -q
python scripts/scan_secrets.py
node scripts/audit.mjs
corepack pnpm exec playwright install chromium
# Linux: PLAYWRIGHT_CHANNEL=chromium; Windows usa Edge installato.
corepack pnpm exec playwright test
python scripts/vendor.py
python scripts/package.py
python scripts/verify_package.py artifacts/deckpilot-0.1.0.zip
# Soltanto Linux CPython 3.11: smoke del pacchetto estratto isolato
python scripts/verify_package.py artifacts/deckpilot-0.1.0.zip --runtime
```

`corepack pnpm preview` serve l'anteprima offline su 127.0.0.1:5173: risposte sintetiche, controlli errore/attesa e componenti DOM per revisione. La produzione usa veri componenti Decky. Anteprime e focus da tastiera non certificano il controller Steam. I test backend bloccano la rete provider e usano dati sintetici, senza chiavi reali.

[Risultati](docs/TEST_PLAN.md), [fonti API](docs/API_VERIFICATION.md), [checklist hardware](docs/HARDWARE_VALIDATION.md), [handoff](docs/CODEX_HANDOFF.md). La documentazione tecnica pubblica è in inglese.

## Pacchetto e futura verifica hardware

Lo ZIP installabile contiene una sola radice DeckPilot/, frontend/backend, entrambi i cataloghi e la wheel Pillow Linux x86_64 CPython 3.11 completa con hash/licenze. Lo ZIP sorgenti riflette la revisione committata. Gli SHA256 sono accanto agli archivi: artefatti di revisione, nessuna release pubblicata.

Prima dell'installazione futura verifica ABI Python Decky, SteamOS/glibc, UID e Loader con la checklist. Se desiderato, usa il flusso ZIP del menu sviluppatore del Loader installato. Nessuno script installa o modifica SteamOS; nessun dispositivo, mini PC, store o release è stato usato.

## Dati e problemi comuni

Nessuna telemetria o server centrale DeckPilot. Consensi provider, immagini, endpoint Ollama e Speech separati. Chiavi in file backend privati in chiaro (0700/0600 POSIX), mai restituite da RPC o salvate nel browser. Software con lo stesso accesso locale può leggerle.

Cronologia in memoria salvo scelta esplicita: 100 messaggi/gioco, sette giorni, 20 giochi e 1,8 MB totali. Cancellare la conversazione conserva le chiavi. Cancellare i dati locali elimina impostazioni/chiavi/storia, ma conserva gli originali importati dall'utente. La disinstallazione Loader può conservare impostazioni: cancellale prima esplicitamente. Cancellazione locale/annullamento non ritirano dati già inviati e non garantiscono rimborsi.

Se la cattura manca, importa manualmente il gioco. Se il modello non supporta immagini, scegline uno compatibile e rinnova il consenso; rimuovi esplicitamente l'allegato per continuare solo col testo. Se la voce manca, leggi la risposta completa o controlla le impostazioni voce separate. Riprova manualmente dopo errori rete/rate limit. Un archivio corrotto fallisce senza azzerare dati: non allegare mai secrets.json ai bug report.

[Privacy](docs/PRIVACY.md), [sicurezza e audit](docs/SECURITY.md), [architettura](docs/ARCHITECTURE.md), [backlog](docs/BACKLOG.md), [roadmap](docs/ROADMAP.md).

Licenza BSD-3-Clause; attribuzione Steam Deck Homebrew e licenze dipendenze nelle [notices](docs/THIRD_PARTY_NOTICES.md). DECKPILOT_CODEX_SPEC.md originale italiano è conservato come base storica; richieste successive riportate nell'handoff sostituiscono lingua e layout predefiniti.
