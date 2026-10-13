# Codex — backend e test automatici, 13 ottobre 2026

## Consegna per Grok

Branch esclusivo: `codex/backend-import-safety-20261013`.
Worktree: `/home/accorsiluca/work/decky-pilot-codex-backend-20261013`.
Base locale/remota verificata con fetch e ls-remote:
`19de5071b5b7f42a7cfa557c62c1d8dd36706a1f`, branch
`codex/decky-pilot-safe-capture-20261013`.
Commit implementazione e regressioni: `43e2b12`.
Il commit successivo contiene soltanto questo resoconto; l'hash finale e la verifica
remota sono registrati in `~/work/decky-pilot-coordination/CODEX.md`.

Il checkout condiviso era pulito, senza worktree Codex precedenti. Nessun cambio branch,
stash, reset o modifica al checkout condiviso. Letti AGENTS applicabili, WORK_CHECKPOINT,
HANDOFF-2026-10-13 e CAPTURE_VERIFICATION. Non ripetuta l'analisi Gamescope già documentata.
CLAUDE.md è comparso durante il lavoro: frontend lasciato interamente a Claude.
GROK.md e TASK-CODEX.md non presenti alle letture effettuate. Scritto soltanto CODEX.md
nella directory di coordinamento. Nessun altro agente avviato.

## Difetti riprodotti e correzioni

1. **Un thread di decodifica sopravvive alla cancellazione dell'RPC.** Prima, il worker
   chiamava `self.images.prepare` e modificava direttamente lo stato condiviso. Annullando
   la richiesta durante il decoding e poi revocando il consenso, cambiando gioco,
   eliminando i dati o chiudendo il servizio, il completamento del worker ripopolava
   l'immagine già cancellata. Otto regressioni upload/import riproducevano il problema.
   Ora il worker prepara un contenitore isolato: soltanto l'RPC ancora attivo trasferisce
   il risultato nello stato condiviso sotto il lock. La chiusura del servizio impedisce
   anche il successo tardivo di una richiesta non cancellata.
2. **L'immagine manuale veniva rifiutata dopo l'accesso a credenziali/cataloghi.** Immagini
   non approvate, mancanti, destinate a un modello diverso, obsolete o con consenso
   disabilitato arrivavano al recupero credenziali prima del rifiuto. Quindici regressioni
   con Ollama, ChatGPT e Grok simulati lo riproducevano. `Images.validate_send` ora effettua
   il controllo prima degli effetti provider, senza consumare l'immagine. `take` ripete
   gli stessi controlli dopo gli await: rimozione o scadenza intervenute nel frattempo
   impediscono comunque l'inferenza.

Nessuna acquisizione privata o trasmissione reale osservata: le riproduzioni usano
esclusivamente immagini sintetiche, sincronizzazione esplicita dei thread e provider finti.
L'ordine precedente consentiva effetti di autenticazione/catalogo, non dimostrava invio
dell'immagine senza approvazione.

## File coinvolti

- `backend/images.py`: validazione dell'invio riutilizzabile e non distruttiva.
- `backend/service.py`: controllo anticipato; preparazione isolata per upload, import e
  percorso di cattura esplicita già disabilitato in produzione.
- `tests/backend/test_image_admission_safety.py`: 29 nuovi casi, inclusi cancellazione,
  chiusura durante decoding, rimozione/scadenza durante admission, import senza provider,
  PNG troncati/animati e limite di dimensione. Un import invalido conserva la precedente
  anteprima valida; la rimozione elimina lo stato del plugin e preserva il file dell'utente.
- `tests/backend/test_capture_safety.py`: quattro nuovi casi di cleanup con writer sintetico
  su errore, timeout simulato, file eccessivo e cancellazione. Override del gate soltanto
  nei test del vecchio adapter; nessun processo/compositor reale viene invocato.
- `docs/agents/CODEX-HANDOFF.md`: questo documento. Handoff canonico non modificato.

## Verifiche eseguite

Ambiente locale: Python 3.14.8 in `.venv`, dipendenze da requirements-dev.txt;
Node 24.20.0 locale in `artifacts/toolchain` (checksum dell'archivio confrontato con
SHASUMS256 ufficiale), pnpm 10.28.2, installazione frozen. Node globale 26 non usato
per i controlli e non modificato. Nessuna dipendenza o lockfile cambiati.

| Verifica | Esito |
| --- | --- |
| Riproduzioni prima della correzione | 23 fallimenti attesi sui due difetti |
| Suite backend locale | 246 passati, nessuno skip (213 esistenti + 33 nuovi) |
| Suite backend su mini-PC isolato | 246 passati, nessuno skip |
| Ruff locale e mini-PC | passato |
| pnpm verify locale | passato: ESLint, TypeScript, 27 frontend, 13 tooling, build Rollup |
| Scan segreti sorgenti | passato, valori mai stampati |
| git diff --check | passato |
| SHA-256 dei quattro file implementazione/test | identici fra worktree e copia mini-PC |

La suite completa è stata seguita da 15 test capture safety verdi in entrambi gli
ambienti dopo un aggiustamento esclusivamente al test per Ruff ASYNC230. Nessun cambio
successivo ai sorgenti di produzione. Nelle prime verifiche dei nuovi test tre fallimenti
erano dovuti al fixture provider `"none"` invece del valore previsto `None`: fixture
corretto e controllo esplicito della risposta settings aggiunto. Nessun errore residuo.

Comandi riproducibili dalla radice del worktree:

```bash
.venv/bin/python -m pytest -q --tb=short
.venv/bin/python -m ruff check backend main.py scripts tests/backend
.venv/bin/python scripts/scan_secrets.py
export PATH="$PWD/artifacts/toolchain/node-v24.20.0-linux-x64/bin:$PATH"
export COREPACK_HOME="$PWD/artifacts/corepack"
corepack pnpm install --frozen-lockfile
corepack pnpm verify
git diff --check
```

Mini-PC: copia dei soli sorgenti versionati più i nuovi test in
`/srv/dev/scratch/decky-pilot-codex-backend-20261013-gG5mVf`, con venv proprio e Python
3.14.8. Directory conservata per riproduzione. Nessun uso dei dati del plugin installato,
nessuna modifica a servizio, sessione grafica, rete/firewall, autostart o pacchetti globali.
L'offline fixture blocca DNS e il trasporto HTTP di produzione; i test di protocollo usano
socket sintetici locali. Nessuna richiesta AI reale.

## Limiti e integrazione

`CAPTURE_SAFETY_VALIDATED=False` invariato; cattura automatica e diretta di produzione
restano disabilitate. I test esistenti confermano gate chiuso anche con cache incoerente,
rifiuto prima di credenziali/cataloghi e impossibilità di consenso automatico visuale.
Le nuove prove di cleanup non validano il vincolo atomico del compositor e simulano
il timeout del writer, non un timeout hardware.

Non eseguiti test grafici/hardware, browser Playwright, packaging/runtime CPython 3.11 o
prove account reali in questa sessione. pnpm verify copre il frontend della base, non
le modifiche parallele di Claude. L'integrazione fra branch e la sessione grafica restano
al coordinatore; nessun merge effettuato. Nessun blocco di autenticazione incontrato.
Nessuna release, pubblicazione applicativa o richiesta upstream nuova.
