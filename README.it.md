# Decky Pilot

> **Il tuo copilota AI per Steam Deck. Ricevi aiuto adatto al tuo gioco, alla tua schermata e al momento in cui stai giocando.**

**Il nostro obiettivo di prodotto.** L’MVP è in revisione. Aiuto contestuale, collegamenti degli account e cattura automatica durante il gioco non sono ancora validati su Steam Deck. Questa pagina distingue implementazione, verifiche eseguite e lavoro restante.

<p align="center"><img src="assets/brand/decky-pilot-logo-dark.png?raw=true" alt="Logo Decky Pilot" width="320"></p>

[English](README.md) · [Galleria UI](docs/UI_GALLERY.md) · [PR MVP #1](https://github.com/realfulvio/decky-pilot/pull/1) · [PR galleria #2](https://github.com/realfulvio/decky-pilot/pull/2)

![Illustrazione concettuale di Decky Pilot: un puzzle su una console immaginaria collegato ad analisi, chiarimenti e voce](assets/presentation/cover-v2.png?raw=true)

*Illustrazione concettuale generata con AI. Non è una fotografia del dispositivo, uno screenshot dell’applicazione o un test Steam Deck.*

> **Presentazione pubblica, MVP nelle PR.** `main` contiene README, immagini e documentazione di presentazione. Il codice applicativo resta nelle PR aperte. Non sono stati effettuati merge, release o pubblicazione nello store Decky. La cattura automatica è disabilitata; l’importazione manuale è un’alternativa, non il completamento della funzione.

## Come funziona

![Flusso concettuale: conferma del gioco, Help me now, consensi separati, contesto recente e aiuto utile](assets/presentation/how-it-works-v2-it.svg?raw=true)

1. **Identifica il gioco.** Usa il titolo Steam attivo quando disponibile, poi conferma o correggi. Per giochi non Steam o riconoscimento incerto, aggiungi il titolo manualmente.
2. **Premi Help me now.** Spiega cosa vuoi ottenere o cosa hai già provato.
3. **Scegli cosa condividere.** Il consenso alla cattura è separato dall’invio alla tua AI. Il percorso attuale usa un PNG/JPEG importato manualmente, un’anteprima ripulita e approvazione per immagine. Per la cattura automatica servono ancora un’integrazione sicura sul solo gioco e verifiche sul dispositivo.
4. **Ricevi aiuto per questo momento.** L’assistente combina immagine recente, titolo e conversazione. Separa osservazioni visibili e deduzioni, offre passi concreti oppure una breve domanda. La tua risposta entra nel contesto della sessione.
5. **Ascolta, se vuoi.** Leggi la risposta o usa la voce facoltativa. Le soluzioni complete sono la preferenza spoiler iniziale; il popup dura sei secondi per impostazione predefinita.

Il diagramma illustra il flusso completo previsto. Le immagini non rivelano missioni, inventario o progressi nascosti. I suggerimenti automatici richiedono contesto recente e utile, almeno 90 secondi di intervallo, niente immagini/consigli duplicati o richieste sovrapposte; nei menu, caricamenti o scene incerte riconosciuti si astengono. Indicatore di sessione e comando Pausa sono implementati, ma la cattura in produzione resta bloccata.

## Cosa funziona oggi

**Significato degli stati:** “Available” indica verifiche nel percorso browser/backend offline sul branch MVP, non un plugin rilasciato o certificato sul dispositivo. “Implemented — awaiting Steam Deck validation” indica codice e test di protocollo simulati, con accettazione hardware ancora NOT RUN. “Planned” indica lavoro ancora necessario.

| Funzione | Stato | Evidenza e limite pratico |
|---|---|---|
| UI inglese iniziale, italiano completo e lingua dell’assistente/voce separata | Available | Rendering React reale, test di localizzazione e impaginazione. |
| Titolo, obiettivo e conversazione della sessione manuali | Available | Titoli non Steam/sconosciuti, correzione e reset verificati. |
| Importazione manuale, anteprima ripulita, approvazione del destinatario | Available | Validazione PNG/JPEG, rimozione metadati, uso singolo e freschezza di 45 secondi verificati. Selettore sul dispositivo da provare. |
| Rilevamento Steam e cambio gioco | Implemented — awaiting Steam Deck validation | Solo informazioni Steam/Decky controllate; incertezza sospende l’automatismo. Controller/dispositivo da verificare. |
| Analisi contestuale, passi concreti e un chiarimento | Implemented — awaiting Steam Deck validation | Risposte visive strutturate validate; osservazioni e deduzioni distinte; risposte conservate nella sessione. Qualità dei modelli reali non valutata. |
| OAuth ChatGPT, API, cataloghi e controllo immagini | Implemented — awaiting Steam Deck validation | Integrazioni native e test offline. Autorizzazioni e inferenza con account reali NOT RUN. |
| Adattatore di cattura, consenso di sessione, scheduler e pausa immediata | Implemented — awaiting Steam Deck validation | Comando Gamescope e test simulati; acquisizione in produzione disabilitata. |
| Acquisizione atomica sicura del solo gioco e cattura automatica attiva | Planned | I controlli di focus non escludono schermate sensibili durante una transizione. È un blocco centrale, non risolto dall’importazione manuale. |
| Popup di sei secondi e voce locale/online facoltativa | Implemented — awaiting Steam Deck validation | Ripiego testuale, consensi e cancellazione verificati; QAM/controller/audio da provare. |
| Login consumer Claude, Gemini o Grok | Planned | Non è stato accertato un flusso compatibile con piani consumer per terze parti; nessun login inventato. |

## Scegli la tua AI

Le integrazioni seguenti sono implementate nella PR MVP con servizi simulati nei test. **Non sono stati eseguiti accessi reali, inferenza API a pagamento o test dei provider su Steam Deck.** I nomi dei modelli arrivano dal servizio scelto; non viene promesso accesso a GPT-5.6/GPT-6.1. Disponibilità e capacità visiva sono controlli separati.

| Provider / collegamento | Collegamento e utilizzo | Requisiti immagini |
|---|---|---|
| **Piano ChatGPT** | OAuth ufficiale locale/open source **Continua con ChatGPT**. Account/workspace idoneo e permesso al piano necessari. Rinnovo/disconnessione backend; catalogo dell’account. Valgono limiti e impostazioni delle app ChatGPT. | Modello restituito dal catalogo con supporto immagini verificato separatamente. Modelli sconosciuti solo testuali. |
| **API OpenAI — avanzato** | Chiave API sviluppatore; `/v1/models` e Responses. **Fatturazione API separata**, non accesso all’abbonamento ChatGPT. | Selezione dal catalogo reale e identificativo visivo esatto verificato. |
| **Claude** | Chiave API della Console Claude, Models e Messages. Fatturazione/limiti API; chiave di un solo workspace. Nessun login consumer. | Modello visivo esatto verificato; identificativi sconosciuti solo testuali. |
| **Gemini** | Chiave AI Studio e quote/fatturazione del progetto. Gli abbonamenti consumer Google non stabiliscono accesso API. | Modello generateContent restituito dal servizio con supporto immagini verificato. |
| **Grok** | Chiave API xAI ufficiale, catalogo dei modelli linguistici e Responses. Account/crediti e condizioni API separate; nessuna equivalenza con abbonamenti consumer. | `input_modalities` restituito deve contenere `image`. Nessuna sostituzione con modelli di generazione immagini. |
| **Ollama** | Endpoint locale/LAN autorizzato e modello installato. La modalità locale supportata non richiede chiavi; il server può a sua volta inoltrare al cloud. | `/api/show` deve indicare `vision` prima dell’invio. |

Le richieste di catalogo sono esplicite e non inviano testo o immagini del gioco; l’accesso ChatGPT recupera anche il catalogo dell’account. Cataloghi parziali sono segnalati. Nessun cambio automatico di modello/provider o ripiego a pagamento dopo gli errori. [Fonti ufficiali, implementazione e verifiche mancanti →](docs/PROVIDER_VERIFICATION.md)

## L’interfaccia

**Screenshot reali del browser con l’App React, controlli HTML dichiarati e dati sintetici.** Mostrano UI implementata, non acquisizioni Steam Deck, risposte AI reali o cattura hardware funzionante. In produzione vengono inseriti controlli Decky; l’accettazione con controller resta da eseguire.

### Benvenuto e onboarding

<img src="docs/images/ui/panel-03-onboarding.png?raw=true" alt="Screenshot browser del benvenuto al primo utilizzo" width="420">

### Scelta del collegamento AI

<img src="docs/images/ui/panel-11-ai-connection.png?raw=true" alt="Screenshot browser della scelta AI e configurazione ChatGPT senza account collegato" width="420">

### Consenso separato alla cattura

<img src="docs/images/ui/panel-12-capture-consent.png?raw=true" alt="Screenshot browser del consenso alla cattura con disponibilità simulata" width="420">

*La disponibilità della cattura è simulata in questa schermata. Non dimostra acquisizione hardware.*

### Revisione prima dell’invio

<img src="docs/images/ui/panel-06-image-review.png?raw=true" alt="Screenshot browser di un’immagine sintetica con permesso separato all’invio al destinatario" width="420">

### Help me now e contesto

<img src="docs/images/ui/panel-01-play.png?raw=true" alt="Screenshot browser di Help me now e osservazioni contestuali sintetiche" width="420">

### Prossimi passi concreti

<img src="docs/images/ui/panel-15-contextual-answer.png?raw=true" alt="Screenshot browser di osservazioni sintetiche, deduzioni esplicite e passi concreti" width="420">

### Un chiarimento utile

<img src="docs/images/ui/panel-13-clarification.png?raw=true" alt="Screenshot browser di una scena ambigua simulata e una breve domanda" width="420">

### Lingue indipendenti e impostazioni

<img src="docs/images/ui/panel-05-languages.png?raw=true" alt="Screenshot browser delle lingue dell’interfaccia e dell’assistente" width="420">

### Voce facoltativa

<img src="docs/images/ui/panel-10-voice.png?raw=true" alt="Screenshot browser della voce locale e OpenAI autorizzata separatamente" width="420">

*I controlli vocali sono UI reale; l’anteprima non riproduce voce.* [Tutte le quindici viste e provenienza →](docs/UI_GALLERY.md)

## Installazione e anteprima sviluppatore

L’MVP è su `codex/deckpilot-mvp`, **non su `main`**. Non c’è una release nello store o un’installazione validata. ZIP e SHA256 di revisione sono [artefatti CI](https://github.com/realfulvio/decky-pilot/actions), non una raccomandazione per la produzione.

```sh
git clone --branch codex/deckpilot-mvp https://github.com/realfulvio/decky-pilot.git
cd decky-pilot
corepack pnpm install --frozen-lockfile
corepack pnpm preview
```

Usa Node 24.20.0 e pnpm 10.28.2. L’anteprima `http://127.0.0.1:5173` usa risposte sintetiche; le dimostrazioni di accesso/cattura non autorizzano account, non eseguono inferenza e non acquisiscono il dispositivo. Restano frontend React/TypeScript e backend Python separati. [Build, packaging e installazione manuale per revisione](https://github.com/realfulvio/decky-pilot/blob/codex/deckpilot-mvp/docs/DEVELOPMENT.md).

## Privacy, credenziali e limiti

Nessuna telemetria o server centrale Decky Pilot. Chiavi e token OAuth restano nei file locali protetti del backend e non vengono restituiti nello stato. I file sono in chiaro con permessi Unix riservati al proprietario, non storage cifrato; software con gli stessi privilegi può leggerli. Non vengono letti cookie del browser o credenziali di altre applicazioni. La disconnessione tenta la revoca remota; eventuale fallimento è segnalato e i token locali vengono cancellati.

La cronologia resta in memoria, salvo consenso alla persistenza. Le immagini vengono ripulite, usate una volta, escluse dalla cronologia e limitate a una copia in attesa. Dopo 45 secondi dalla preparazione un’immagine non può essere inviata come contesto corrente; l’importazione non verifica quando il file originale sia stato catturato. Cattura e invio hanno consensi distinti. Cambio di destinatario/account o revoca annullano il lavoro pendente. La cancellazione locale non ritira dati già inviati al provider.

Le richieste automatiche hanno almeno 90 secondi di intervallo, budget di 20 tentativi per sessione, attesa dopo limiti e pausa dopo errori ripetuti. L’anteprima ChatGPT richiede streaming e non accetta un limite di token di uscita lato server; i limiti locali non garantiscono un tetto di fatturazione. Controlla [utilizzo delle app ChatGPT](https://chatgpt.com/settings/usage) e quote API. Speech online usa chiave API OpenAI e consenso separati e può avere costi propri; il login al piano ChatGPT non autorizza Speech.

[Privacy](https://github.com/realfulvio/decky-pilot/blob/codex/deckpilot-mvp/docs/PRIVACY.md) · [Sicurezza](https://github.com/realfulvio/decky-pilot/blob/codex/deckpilot-mvp/docs/SECURITY.md)

## Verifiche e roadmap

Le suite offline coprono OAuth, rinnovo/revoca, cataloghi, richieste xAI, modelli senza visione, consenso revocato, immagini obsolete, cambio gioco, ambiguità, chiarimenti, duplicati e intervalli automatici. Il browser verifica impaginazione e focus da tastiera. La CI Linux crea il pacchetto e prova il runtime crittografico/Pillow estratto. Sono **servizi simulati e verifiche locali reali**, non certificazione dei provider o del dispositivo.

Prossimi passi: acquisizione atomica sicura del solo gioco e rifiuto di schermate Steam/QAM/accesso/account; account reali, cataloghi, limiti e inferenza visiva; poi installazione/ABI Steam Deck, controller, giochi non Steam, transizioni, sospensione/ripresa, voce e prestazioni. Vedi [checklist hardware](https://github.com/realfulvio/decky-pilot/blob/codex/deckpilot-mvp/docs/HARDWARE_VALIDATION.md), [blocco cattura](https://github.com/realfulvio/decky-pilot/blob/codex/deckpilot-mvp/docs/CAPTURE_VERIFICATION.md) e [evidenze dei test](https://github.com/realfulvio/decky-pilot/blob/codex/deckpilot-mvp/docs/TEST_PLAN.md).

[Provenienza immagini](docs/PRESENTATION_ASSETS.md) · [Revisione pubblicazione](docs/PUBLICATION_REVIEW.md) · [Licenza BSD-3-Clause](https://github.com/realfulvio/decky-pilot/blob/codex/deckpilot-mvp/LICENSE)
