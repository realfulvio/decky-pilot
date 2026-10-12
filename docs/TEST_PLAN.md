# Test e risultati

Verifica locale 12 ottobre 2026, Windows workstation, Node24.20.0/pnpm10.28.2/Python3.13. Il target Linux CP311 è incluso nel pacchetto ma non eseguibile su Windows. WSL non installato, Docker non disponibile: nessuna validazione Linux/SteamOS dichiarata. GitHub Actions predisposto ma non osservato senza remote del progetto.

| Comando | Risultato locale | Copertura |
|---|---|---|
| `pnpm install --frozen-lockfile` | PASS | Versioni e integrità lockfile |
| `pnpm lint` / `pnpm typecheck` | PASS | ESLint e tipi rigorosi |
| `pnpm test` | PASS, 11 test | Onboarding, chiave pulita, manuale, pending/cancel, errori, preview/approvazione, contratto, toast, Steam shape, listener/sessioni, TTS no replay, audio cleanup |
| `python -m ruff check backend main.py scripts tests/backend` | PASS | Backend/lifecycle/scripts/test |
| `python -m pytest -q` | PASS,116 test;2 SKIP | Quattro protocolli/vision/errori, default/range/migrazione/corruzione/atomicità, sessioni/lock, clock0/89/90/resume/pause/dedup/errori, immagini/TTL/consensi, TTS/stop/revoca/SSRF/import/contratto/lifecycle |
| `pnpm exec playwright test` | PASS,2 test | Edge: chat/contesto/focus Tab/Stop visibile, no overflow/errori, preview1280×800/720 |
| `python scripts/scan_secrets.py` | PASS | Nessun match, valori non stampati |
| `node scripts/audit.mjs` | PASS con1 advisory high ammesso dalla policy | `braces` build-only senza patch upstream: vedere SECURITY. Non audit clean |
| `pnpm build` | PASS | Rollup WASM4.64.5, React esterna, nessun harness |
| `python scripts/vendor.py` | PASS | SHA256 wheel Pillow Linux CP311 |
| `python scripts/package.py` / `verify_package.py` | PASS | Layout/allowlist/manifest/runtime/licenze/checksum; hash finali nei file accanto al ZIP |

I2 SKIP sono test symlink: Windows non permette di crearli in questa sessione. Il workflow Linux esegue gli stessi test, controlla mode0700/0600 e importa Pillow vendorizzata. Il ramo permessi POSIX è da eseguire in Linux; non è verificato dai mock Windows.

## Determinismo

Fixture backend blocca DNS e l'entry point del trasporto produzione. Asyncio Windows usa socketpair loopback per wakeup, distinto da una chiamata provider. Test del worker HTTP reale sostituiscono DNS/socket/HTTP e verificano IP pinned, dimensioni e redirect rifiutati. Tutte le immagini/risposte/credenziali fixture sono sintetiche, nessun egress provider.

Adapter reali in produzione, trasporti iniettati nei test. Verificati request native/auth/output/usage,401/403/404/429/5xx,timeout,risposta vuota/bloccata/malformata e nessuna esposizione di body d'errore. Ollama vision controlla /api/show, senza pull. Fixture JSON Schema validate da Python e Ajv; eventi/result backend effettivi nello stesso schema.

Ancora da eseguire: CI remota/import CP311 Linux, live smoke con consenso esplicito e chiavi separate se richiesto, [checklist Steam Deck](HARDWARE_VALIDATION.md). Le preview HTML sono harness dichiarato con controlli DOM; produzione usa componenti Decky. Non equivalgono a rendering Steam/controller reale.
