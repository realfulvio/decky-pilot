# Claude Code — handoff frontend e percorso manuale immagini

## Esito riferito da Grok (nota di chiusura, 13 ottobre 2026)

Riferimento per la ripresa: branch `grok/decky-pilot-integrate-20261013`, checkpoint
`c2a296d32fa37f3ce7eac767aacae56bbe8c3983` (contiene `c79ce2b` e i commit di Codex).

- **Osservato da Grok** sul Quick Access reale del mini-PC (non la Deck), come comunicato a me:
  anteprima presente dopo il selettore, avviso senza destinatario, rimozione persistente,
  layout non tagliato. Non l'ho osservato io né ho rieseguito test dopo `c79ce2b`.
- **Non verificati:** D-pad fisico e Steam Deck.
- **Solo simulato da me** (vitest/Playwright, harness offline): il modello della colonna
  (rotaia 56 px, padding, `nowrap`) era un'ipotesi; la causa reale del ritaglio non è stata
  misurata da me e non so quale parte delle modifiche CSS sia stata necessaria.

## Aggiornamento 2: anteprima persa dal selettore, ritaglio (13 ottobre 2026, notte)

Branch `claude/decky-pilot-frontend-20261013`. Commit nuovo: `6bc33dd` (più questa nota).
Backend, gate (`CAPTURE_SAFETY_VALIDATED = False`) e sessione grafica non toccati; nessuna richiesta AI.

**Pacchetto provato da Grok:** base `19de507`, quindi **senza** `eda133c`, `1718eb5` e senza i commit
backend di Codex (lo dice l'handoff di Grok `f8033d8`; non ho ispezionato il pacchetto installato).
La prova reale non dice nulla sulla versione corretta.

### Causa (dal codice, riprodotta nei test, non misurata sul mini-PC)

1. `image`, `approved`, `imageError` erano `useState` in `Chat`. Decky toglie il pannello dal
   documento mentre `openFilePicker` è aperto: la promessa del picker si risolve, la
   `prepare_import_image` parte (una sola, come visto), ma l'esito finisce in `setState` di un
   componente smontato e si perde. Nessuna anteprima, nessun errore.
2. Aggravante: il cleanup di `Chat` all'unmount chiamava `discard_image`. Anche se l'esito fosse
   stato conservato, il rimontaggio avrebbe trovato l'immagine già scartata sul backend.
3. Il `Controller` invece è creato in `definePlugin` e vive oltre i mount del pannello
   (`onDismount` lo chiude solo quando il plugin viene scaricato): è il posto giusto per lo stato.

### Correzione (`src/services/controller.ts`, `src/components/App.tsx`)

- Slot immagine nel controller: `view.image = {image, approved, error, busy}`.
  Metodi: `importImage(pick)`, `prepareImage(method, payload, before)`, `approveImage()`,
  `clearImage()`. Il selettore e la cattura (chiusura menu + attesa 700 ms) usano lo stesso slot.
- Invalidazione: cambio sessione/revisione, consenso immagini, provider o modello; riferimento
  non più in `pendingImageRef` del backend. Un risultato in ritardo per contesto vecchio viene
  scartato (`discard_image`). Scarto anche a `controller.close()`, **non** più all'unmount.
- «Rimuovi immagine» → `clearImage()` (una sola `discard_image`). Dopo l'invio la scheda si chiude
  senza scarto (immagine consumata).
- Mentre il file viene preparato il pulsante «Aggiungi immagine» resta disabilitato, anche dopo
  un rimontaggio.

### Layout

Causa del ritaglio sul Quick Access reale **non misurata** (la sessione grafica è di Grok). Ipotesi
coerente con il sintomo: i pulsanti Decky aggiungono padding orizzontale e tagliano le etichette
`nowrap`; la griglia a 3 colonne fissa lasciava a «Impostazioni» meno spazio del testo.
Cambiamenti in `styles` (nessuna funzione o opzione tolta): tab e righe di azioni in `flex-wrap`
(vanno a capo invece di essere tagliate), etichette dei pulsanti a capo, `.dp` con larghezza 100%,
`min-width:0` e piccolo margine iniziale (6 px). Nessun container query né `contain`, per non
rischiare di collassare la larghezza nel contenitore reale.

### Prove nuove (che fallivano sul codice precedente dove indicato)

| Prova | Cosa copre |
| --- | --- |
| vitest «keeps the prepared image across a panel unmount while the file picker is open» (fallisce prima) | smonta durante il picker in sospeso, risolve, rimonta: anteprima, avviso destinatario, «Rimuovi», nessun `discard_image` all'unmount, una sola alla rimozione |
| vitest «shows the preparing state after a remount…» (fallisce prima) | rimontaggio mentre il file non è ancora preparato |
| vitest «drops a prepared image when the game session changes…» (fallisce prima) | risultato tardivo per sessione vecchia scartato |
| Playwright `/?picker=1`: pannello rimosso dal documento durante il selettore simulato | il flusso osservato da Grok, con `aside` assente (`toHaveCount(0)`) e ritorno con anteprima |
| Playwright `/?picker=1&qam=1`: colonna 300 px con rotaia da 56 px | nessun elemento fuori dal contenitore, nessun testo che esce dal proprio rettangolo (misurato con `Range`), inglese e italiano, tutte le schede; il test falliva con il CSS precedente |

Limiti: il modello della colonna (rotaia 56 px, padding, `nowrap`) è un'**ipotesi** nel harness
(`index.html`, opt-in `?qam=1`), non il DOM reale. Il picker simulato smonta il pannello ma non è
`openFilePicker` di Decky. `pnpm verify` verde (vitest 35, tooling 13, build), Playwright 9/9
(Chromium locale), pytest backend 213/213 invariato, scan segreti e `git diff --check` verdi.

### Per la nuova prova di Grok (non la eseguo io)

1. Costruire il pacchetto da **questo** branch. Per includere anche i fix backend di Codex serve
   un'integrazione di prova a parte (un merge di prova tra i due branch non dà conflitti, verificato
   con `git merge-tree`); questo branch non contiene `43e2b12`. Ricontrollare i commit del pacchetto.
2. Stessi passi 1-5 (Test/prova, solo immagini consentite, provider assente, selettore, PNG
   sintetico, nessun invio). Attesi al ritorno del pannello: anteprima, «Nessun servizio AI
   scelto…», «Consenti l'invio» disabilitato, «Rimuovi immagine» funzionante, nessun errore.
3. Misura **in sola lettura** nel Quick Access reale, da DevTools, prima e dopo l'installazione:

```js
(() => { const q = el => el && (r => ({l: Math.round(r.left), r: Math.round(r.right), w: Math.round(r.width)}))(el.getBoundingClientRect());
  const dp = document.querySelector('.dp'); const out = {viewport: innerWidth, dp: q(dp), chain: []};
  for (let e = dp; e && e !== document.body; e = e.parentElement) { const c = getComputedStyle(e);
    out.chain.push({tag: e.tagName, cls: String(e.className).slice(0, 50), ...q(e), ov: c.overflowX, pl: c.paddingLeft, ml: c.marginLeft}); }
  out.nav = [...dp.querySelectorAll('.dp-nav button')].map(b => ({t: b.textContent, ...q(b), ws: getComputedStyle(b).whiteSpace, ov: getComputedStyle(b).overflow, sw: b.scrollWidth, cw: b.clientWidth}));
  return JSON.stringify(out); })()
```

   Se il bordo sinistro è ancora tagliato, mandare quel JSON: dirà se la causa è la rotaia (offset di un
   antenato) o il padding dei controlli, e aggiusterò solo quello.
4. Nessun cambiamento backend richiesto. Se in futuro serve recuperare l'anteprima dopo il
   riavvio della pagina JS (non coperto: lo slot è in memoria), servirebbe un RPC che restituisca
   la miniatura di `pendingImageRef`; **non** richiesto ora.

---

## Aggiornamento 1 (13 ottobre 2026, sera)

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
