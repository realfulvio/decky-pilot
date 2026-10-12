# Privacy e controllo dei dati

Nessuna telemetria iniziale. Nessun server centrale DeckPilot. Prima dell'invio la UI espone destinatario e consensi. Default: provider assente, chat remota non autorizzata, auto hint disattivati, immagini disattivate, cronologia persistente disattivata; voce preferita ma condizionata a motore/consenso.

| Percorso | Dati trasmessi | Consenso e revoca | Conservazione locale |
|---|---|---|---|
| Chat cloud | Titolo, AppID se fornito, obiettivo/area/note e recenti messaggi selezionati, domanda | Provider/modello configurati, consenso chat; cambio destinazione revoca e annulla | Cronologia in memoria; persistenza solo opt-in |
| Ollama | Stessi dati all'endpoint autorizzato | Consenso endpoint esplicito; HTTP LAN avviso in UI | Non si assume che il server resti locale o non inoltri al cloud |
| Immagini | Soltanto JPEG ricodificato mostrato in preview | Import abilitato + scelta singola + approvazione per immagine/sessione/provider/modello/endpoint | Una copia effimera, monouso/scadenza 5 minuti; originali importati rimangono file dell'utente nella cartella dedicata |
| Speech OpenAI | Fino a 1.000 caratteri del testo della risposta | Consenso TTS separato e chiave OpenAI; secondo destinatario esplicito se chat usa altro provider | WAV in memoria fino a fine audio/stop; nessun server aggiuntivo |
| espeak-ng | Testo su stdin a processo locale | Preferenza voce e motore disponibile | WAV in memoria; nessuna rete |

Non vengono raccolti SteamID, amici, profilo, libreria, hostname, percorsi locali nel prompt o telemetria macchina. L'AppID non autorizza accesso al gameplay. Il percorso import è mostrato soltanto nella UI locale, non trasmesso al provider.

Le chiavi sono nel percorso settings ufficiale Decky, come file privati **in chiaro** (0700/0600 POSIX, scrittura atomica), mai restituite da RPC e mai mantenute in storage browser. «Salvata» non significa «valida». La cancellazione chiave elimina il valore locale e ferma task/cache pertinenti; software locale compromesso può comunque accedere al processo/file. Non c'è una promessa di keyring o cifratura non implementata.

Cronologia: memoria per sessione; con persistenza, massimo 100 messaggi per gioco, 7 giorni, 20 giochi/1,8 MB complessivi con evizione. Scadenza al load e ogni tick backend 5 s. «Cancella cronologia di questo gioco» elimina memoria e voce/immagini pendenti e la storia su disco di quel gioco, mantenendo chiavi. «Cancella tutti i dati locali» elimina chiavi/configurazione/storie, interrompe task e svuota copie temporanee; **non** elimina gli originali che hai copiato nella cartella import. Eliminali manualmente se desiderato. Uninstall può mantenere settings/chiavi secondo Loader: usa cancellazione esplicita prima di rimuovere il plugin.

La cancellazione locale non cancella messaggi già inviati, non revoca lavoro già iniziato dal provider e non garantisce rimborsi. `store:false` OpenAI non equivale a zero retention. Piano/account/contratto influenzano trattamento e conservazione: consulta [OpenAI data controls](https://developers.openai.com/api/docs/guides/your-data), [Gemini terms](https://ai.google.dev/gemini-api/terms), [Claude privacy](https://privacy.claude.com/) e le condizioni del server Ollama scelto. Nessuna promessa uniforme di gratuità o mancato uso dei dati.

Diagnostica: solo limiti e capability/configurazione sanitizzata, nessun prompt/chiave/audio/immagine/risposta o traceback remoto. Rivedila prima della condivisione; template issue non inseriscono dati privati. Fixtures e harness usano dati sintetici.
