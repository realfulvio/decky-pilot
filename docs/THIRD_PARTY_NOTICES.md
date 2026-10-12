# Attribuzioni e licenze

DeckPilot BSD-3-Clause (LICENSE). Configurazione/lifecycle seguono il template Steam Deck Homebrew BSD-3-Clause; copyright2022–2024 mantenuto in LICENSE. Nessun walkthrough/asset proprietario.

| Dipendenza | Uso | Licenza/distribuzione |
|---|---|---|
| @decky/api1.1.3 | Bridge bundled | LGPL-2.1; testo completo docs/licenses/decky-api-LGPL-2.1.txt, sorgente corrispondente third_party/decky-api |
| @decky/ui4.12.1 | Runtime Loader esterno | LGPL-2.1,non redistribuito nel ZIP |
| @decky/rollup1.0.2 | Build | BSD-3-Clause,non runtime |
| tslib2.8.1 | Helper TypeScript |0BSD,notice seguente |
| React19.1.1 | Harness; produzione esterna | MIT,non incluso nel ZIP |
| Pillow12.3.0 | Decode/resize | HPND e licenze native in py_modules/pillow-12.3.0.dist-info/licenses/LICENSE,wheel integrale |
| espeak-ng | Processo opzionale | GPL-3.0,binario non installato/copiato/distribuito |
| Toolchain test/build | Sviluppo | Non inclusa nel pacchetto runtime,licenze in dipendenze installate |

tslib notice(0BSD): Copyright(c)Microsoft Corporation. Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted. THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

Le licenze native transitive Pillow sono conservate integralmente nella wheel vendorizzata. Le licenze originali delle librerie bundle sono incluse in docs/licenses. La licenza BSD riguarda i sorgenti DeckPilot; non sostituisce LGPL di Decky API/UI. Il gitHead npm di API1.1.3 coincide con d1b7f16070777a0ada939cbacd3606eeba0574f5, sorgente non modificato incluso in third_party/decky-api e nei due archivi.

La distribuzione locale comprende anche deckpilot-0.1.0-source.zip con sorgenti frontend/backend, lockfile, configurazione e sorgente API: è possibile modificare o sostituire la libreria e ricompilare il plugin seguendo README. Non si impongono limitazioni al reverse engineering per debug delle modifiche della libreria. Per ricollegare una variante, compila third_party/decky-api/src con la configurazione inclusa, installa la variante come dipendenza locale al posto di @decky/api e riesegui pnpm build. Le altre dipendenze/licenze mantengono i rispettivi termini.
