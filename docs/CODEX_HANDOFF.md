# Handoff esecutivo

Repository locale: C:\Users\Admin\deckpilot. Branch: codex/deckpilot-mvp, base locale main con commit iniziale vuoto. La directory iniziale C:\Users\Admin non era un repository e la ricerca non ha trovato deckpilot. Il remote non è configurato: account GitHub collegato accessibile, ma nessun repository deckpilot nell'elenco e URL/percorso richiesto non ancora fornito. Nessun proprietario/remote inventato, nessun nuovo repository remoto creato, nessun push o PR dichiarati.

Specifica letta integralmente prima delle modifiche, copia originale in DECKPILOT_CODEX_SPEC.md. Nessun lavoro preesistente sovrascritto. Nessun SSH/mini PC usato, nessuna installazione su dispositivi, release/store, force push, reset o merge.

Implementazione: UI Decky italiana, dominio Python importabile senza Loader, quattro provider nativi reali, chiavi private/consensi separati, contesto manuale/Steam isolato, sessioni/cancel/idempotenza, scheduler90s, popup6s/crono intera, immagini ripulite/preview/handle monouso, TTS locale/Speech e fallback/Stop, cancellazione/retention, CI/package/docs/backlog.

Verifiche locali:116 test backend passati,2 symlink skip per privilegi Windows;11 frontend;2 browser1280×800/720;Ruff/ESLint/TypeScript/build/scansione/wheel hash e packaging. Vedi TEST_PLAN e API_VERIFICATION. GitHub Actions/import nativo Linux CP311 e hardware NON ESEGUITI. Un advisory high braces build-only è mostrato ed ammesso da policy documentata, non audit clean. La policy Windows blocca il modulo Rollup nativo4.64.5; alternativa ufficiale WASM usata senza cambiare policy.

Artefatti in artifacts: deckpilot-0.1.0.zip e SHA256; source.zip e SHA256; preview1280×800/720; patch e git bundle della consegna. ZIP installabile strutturato DeckPilot/ con wheel CP311 Linux completa/licenze, codice API LGPL corrispondente e nessun file privato/test/venv. Il ZIP non dimostra compatibilità hardware. Gli hash finali sono nei file .sha256 accanto agli archivi (evita riferimenti circolari al proprio hash nel pacchetto).

## Collegamento al remoto mancante

Fornire il percorso del clone corretto o l'URL remote effettivo. Ispezionare default branch, istruzioni AGENTS e modifiche prima di portare i commit locali: se esiste già codice, creare worktree pulito dalla sua base e adattare/cherry-pick le modifiche senza sovrascrivere lavoro. Il branch locale nasce da bootstrap vuoto perché mancava il repository; **non** forzare la storia su una base diversa.

Se il remoto fornito è realmente un nuovo repository vuoto, il proprietario può scegliere di usare questa baseline. Solo dopo aver verificato la destinazione, configurare origin, controllare la base e trasferire il branch con push normale. Per un repository esistente, integrare dalla base appropriata e usare gli stessi controlli. Poi:

```powershell
git remote -v
git fetch origin
git branch -av
# Dopo verifica della base e integrazione non distruttiva:
git push -u origin codex/deckpilot-mvp
gh pr create --base <BASE_VERIFICATA> --head codex/deckpilot-mvp --title 'Implement DeckPilot MVP with secure providers, contextual hints and TTS' --body-file docs/PR_BODY.md
gh pr view --json url,state,baseRefName,headRefName
```

Non usare placeholder come destinazioni reali. Nessun merge. La descrizione PR è concreta in PR_BODY.md; URL da riportare solo dopo verifica. CI remota da osservare e correggere prima della revisione.

## Prossimi gate

1. Remote/push/PR e CI Linux/import Pillow/permessi POSIX.
2. Checklist hardware DP-015/017: versioni/ABI/UID, caricamento/focus/picker/Steam/popup/TTS/IPC/performance reali.
3. Capture DP-016 e streaming/STT/OCR/retrieval solo con verifica/consensi/test dedicati.

Nessuna chiave reale/live smoke è necessario per completare la revisione offline. La disponibilità futura della Deck è input al gate hardware, non motivo per riscrivere il backend come mock.
