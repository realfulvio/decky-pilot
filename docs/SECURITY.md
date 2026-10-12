# Sicurezza

## Confini e minacce

Decky può condividere un ambiente privilegiato con altri plugin. Flags `[]`, host-user rilevato dalla sorgente Loader ma UID/ownership reali ancora da misurare sulla Deck. Nessuna promessa di sandbox forte, cifratura o protezione da altro software locale compromesso.

| Minaccia | Contromisura implementata | Limite |
|---|---|---|
| Leakage chiavi/log | Secrets backend separati, public configured boolean, errore allowlist, nessun body remoto/log contenuti, campi UI puliti dopo save | Memoria/processo e file plaintext accessibili al relativo utente |
| RPC/manipolazione consenso | Allowlist metodo/campi, tipi/range backend, config autoritativa, destinatario non dal payload chat | Altri plugin con accesso al medesimo processo/user non sono considerati una sandbox indipendente |
| Traversal/symlink | Upload di bytes senza path; import solo basename PNG/JPEG sotto radice dedicata, ownership, no symlink nei parent, POSIX O_NOFOLLOW | Nessuna attestazione generale del picker. Attaccante con stesso UID/controllo filesystem può fare race; non promessa di isolamento da tale attaccante |
| SSRF/DNS/redirect | Cloud host fissi HTTPS, Ollama solo endpoint esplicito HTTP(S) senza auth/query/path, risoluzione/rivalidazione di tutti IP e socket pinned, link-local/metadata/CGNAT/translation bloccati, nessun redirect/proxy | LAN/loopback consentiti intenzionalmente. Firewall/tunnel non configurati; resolver OS può ritardare chiusura worker |
| Flood/costi | Una generazione globale, idempotenza locale, deadline/output bounded, hint cooldown server 90 s, contesto fresco, 20 tentativi/sessione, pause dopo 3 errori, zero retry generazioni | Non limite monetario duro, costo di richieste già inoltrate possibile dopo cancel |
| Prompt injection | Policy separata, note/immagini dati non affidabili; nessun tool/shell/retrieval | Il modello può sbagliare o violare la policy spoiler; nessuna garanzia semantica assoluta |
| Immagini/bomb | Decode reale, 5 MiB/20 MP, JPEG/PNG statici, MIME reale, metadati rimossi e resize; monouso TTL300s | Pillow nativo deve essere ABI compatibile e mantenuto aggiornato |
| Shell/audio | subprocess_exec, argv fisso, testo stdin, stdout bounded, timeout/stop, HTMLAudio/object URL revocati | Routing/qualità su hardware non verificati |
| Supply chain | Versioni e lockfile, wheel SHA256, Actions SHA, CI read-only, scansione segreti e audit | Hash non elimina compromissione upstream; toolchain mantenuta con aggiornamenti mirati |

## Audit dipendenze del 12 ottobre 2026

Il template proponeva Rollup 4.53.3. [GHSA-mw96-cpmx-2vgc](https://github.com/rollup/rollup/security/advisories/GHSA-mw96-cpmx-2vgc) è stato corretto usando Rollup WASM ufficiale 4.64.5 per tutte le risoluzioni; build verificata.

Rimane **un advisory high non corretto upstream**: `GHSA-vfj7-8cjw-p6xm`, `braces` 3.0.3 via `@decky/rollup > rollup-plugin-delete > del > globby > fast-glob > micromatch`. [Issue upstream](https://github.com/micromatch/braces/issues/70): ricorsione su pattern annidati. Non è nel bundle/plugin runtime; il preset di build usa soltanto il pattern fisso `./dist/*`, senza pattern provenienti dall'utente. Eccezione circoscritta documentata, **non audit senza vulnerabilità**. `scripts/audit.mjs` ammette solo quell'ID su quel percorso e fallisce qualsiasi nuovo high/critical o audit non disponibile. Rivedere prima di una release o quando esiste una patch; eliminare l'eccezione entro il gate M4. Non usare build config provenienti da fonti non fidate.

ESLint 9 e alcune dipendenze di build riportano deprecazione, distinta da un advisory. Nessun aggiornamento massivo effettuato. Le installazioni di sviluppo possono usare rete per registry/docs; i test predefiniti non usano provider reali. Live smoke richiede consenso e chiave separati, non viene eseguito automaticamente né in CI.

## Storage, cleanup e segnalazioni

Directory POSIX 0700 e file 0600, owner del processo, scrittura temporanea/fsync/replace, schema/versione valida. Windows non replica i permessi POSIX: non usare questa macchina come prova di sicurezza SteamOS. File corrotto/futuro non viene azzerato. Unload e cambio contesto/consenso terminano task/processi/handle/audio; DNS e chiamate remote già spedite hanno cancellazione best effort.

La scansione sorgenti non stampa i match e cerca chiavi/pem comuni, con limiti noti (non dimostra assenza assoluta di segreti). ZIP allowlist esclude settings/secrets/history, cache e venv; API key reali non sono state usate. Per problemi di sicurezza, descrivi categoria e passi con dati sintetici, senza condividere chiavi o contenuti privati.
