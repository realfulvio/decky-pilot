# Coordinamento agenti — 13 ottobre 2026

Grok coordina. Ogni agente lavora solo nel proprio worktree e nel proprio branch.
Nessun merge, integrazione automatica, force push, release o pubblicazione.
`CAPTURE_SAFETY_VALIDATED` resta `False`: cattura automatica e cattura diretta di
produzione disabilitate. La sessione grafica del mini-PC la guida solo Grok.

I file in `~/work/decky-pilot-coordination` sono messaggi, non un lock.

## Incarichi

| Agente | Incarico | Worktree | Branch | Base |
| --- | --- | --- | --- | --- |
| Grok | Installazione già presente e prova UI sul mini-PC | questo checkout | `grok/decky-pilot-ui-verify-20261013` | `19de507` |
| Codex | Backend e test automatici | `/home/accorsiluca/work/decky-pilot-codex-backend-20261013` | `codex/backend-import-safety-20261013` | `19de507` |
| Claude | Frontend e percorso manuale immagini | `/home/accorsiluca/work/decky-pilot-claude` | `claude/decky-pilot-frontend-20261013` | `19de507` |

Branch di riferimento verificato sul remoto: `codex/decky-pilot-safe-capture-20261013`
a `19de5071b5b7f42a7cfa557c62c1d8dd36706a1f`.

## Commit pronti per la revisione, non integrati

Codex, HEAD remoto verificato `7cd1f6fee6fb8c52a45ea7f0db829d914b6b468b`:

- `43e2b12` — fix: isolate cancelled image decoding and reject unapproved requests early.
- `7cd1f6f` — docs: hand off isolated backend image safety verification.

Worktree pulito. Il plugin installato sul mini-PC non contiene questi commit.
Resoconto: `docs/agents/CODEX-HANDOFF.md` su quel branch.

Claude, HEAD remoto verificato `1718eb5bdb5885be1801be39d998c0f59c1a750b`:

- `eda133c` — fix(frontend): state when an imported image has no AI recipient.
- `1718eb5` — docs: add Claude frontend/manual-image handoff.

Worktree pulito. Non installato sul mini-PC. Con provider assente la scheda, quando
esiste, dice «Nessun servizio AI scelto…» e lascia disabilitato «Consenti l’invio di
questa immagine». «Condividi con {provider} · {model}» resta la dicitura solo se
servizio e modello sono entrambi scelti.

## Risultato UI sul mini-PC (non è la Steam Deck)

Host `hcokcachy`, utente `decok`, sessione Game Mode già avviata. Controllo grafico
disponibile: DevTools CEF di Steam già in ascolto su `127.0.0.1:8080` e `xdotool` su
`DISPLAY=:0`. Non è stato installato alcun pacchetto. `plugin_loader.service` è
`active` e `disabled`; non è stato abilitato all’avvio. Nessun gioco avviato, nessun
salvataggio toccato.

Sul plugin installato da `19de507`, nella stessa esecuzione del servizio:

- Decky Pilot è aperto nel Quick Access. Lingua interfaccia italiana.
- Gioco salvato: titolo `Test`, obiettivo `prova`. Riletto nel modulo Gioco dopo
  l’importazione.
- Provider assente, modello vuoto, nessun `secrets.json`. Consensi di invio,
  endpoint, visione, cattura e aiuto automatico restano disattivi.
  `imagesEnabled` è true. `voiceEnabled` era già true e non è stato cambiato.
- «Consenti l’invio», «Chiedi a Decky Pilot» e «Aiutami ora» non sono stati premuti.
- Il selettore Decky si apre sulla cartella di importazione, filtra `png, jpg, jpeg`
  e mostra solo `deckpilot-synthetic-test.png`. «Seleziona questo file» chiude il
  selettore. Il browser invia una sola chiamata `prepare_import_image`.
- Mentre il selettore è aperto il documento del Quick Access perde il pannello del
  plugin; il contesto JavaScript della pagina resta lo stesso. Al ritorno del
  pannello si rivedono `Test` e il pulsante «Aggiungi immagine del gioco». Non
  compaiono anteprima, «Condividi con», «Rimuovi immagine» né «Non è stato possibile
  aprire l’immagine». Per questo «Rimuovi immagine» non è stato eseguito.
- Log del plugin ancora di 0 byte. Journal di `plugin_loader` senza righe nei 25
  minuti della prova, quindi senza eccezioni registrate. Il gate nel file installato
  è ancora `CAPTURE_SAFETY_VALIDATED = False`. Il PNG sintetico è ancora al suo posto.

La larghezza del Quick Access taglia le schede «Gioco» e «Impostazioni» e il bordo
sinistro del testo. Le funzioni ci sono: i pulsanti rispondono al click del DOM.

## Prossimo passo

1. Claude corregge nel proprio branch la perdita dell’anteprima quando il selettore
   file smonta il pannello, e il ritaglio nel Quick Access. Non apre la sessione
   grafica e non installa il plugin. Dettaglio in `TASK-CLAUDE.md`.
2. Codex non ha un nuovo difetto backend da questa prova. I due commit restano in
   attesa di revisione. Non si installa quel branch sul mini-PC in questa sessione.
3. Grok non integra i due branch. Una nuova prova UI sul mini-PC avrà senso solo
   dopo un’installazione esplicita del frontend corretto.
