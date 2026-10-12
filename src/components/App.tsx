import { useEffect, useRef, useState, useSyncExternalStore } from 'react';
import type { GameContext, PreparedImage, ProviderId, Settings } from '../domain/types';
import { validateContext } from '../domain/validation';
import type { Controller } from '../services/controller';
import type { Controls } from './controls';

const providerOptions = [{value: '', label: 'Nessuno'}, {value: 'openai', label: 'OpenAI'}, {value: 'gemini', label: 'Gemini'}, {value: 'claude', label: 'Claude'}, {value: 'ollama', label: 'Ollama'}];
const spoilerOptions = [{value: 'none', label: 'Nessuno spoiler'}, {value: 'hints', label: 'Indizi'}, {value: 'full_solutions', label: 'Soluzioni complete'}];
interface Props {controller: Controller; controls: Controls; detectGame?: () => Partial<GameContext> | null; pickImage?: () => Promise<string | null>}
export function App({controller, controls: C, detectGame, pickImage}: Props) {
  const view = useSyncExternalStore(controller.subscribe, controller.snapshot);
  const [tab, setTab] = useState<'chat' | 'context' | 'settings'>('chat');
  if (!view.status) return <C.Section title="DeckPilot"><p>Caricamento backend…</p><p role="alert">{view.error}</p><C.Button onClick={() => { void controller.refresh(); }}>Riprova</C.Button></C.Section>;
  const status = view.status;
  return <div style={{fontSize: 16, lineHeight: 1.5, color: '#f2f5f8', display: 'flex', flexDirection: 'column', maxHeight: '72vh'}}>
    <div style={{flexShrink: 0}}><C.Section title="DeckPilot">
      <p>{status.context?.title ?? 'Imposta il gioco'} · {status.context?.source === 'steam_internal' ? 'Steam (interno)' : status.context?.source === 'unknown' ? 'Contesto non confermato' : 'Contesto manuale'}</p>
      <p>{status.settings.provider ?? 'Provider non configurato'} · {spoilerOptions.find(o => o.value === status.settings.spoiler)?.label}</p>
      <p>{view.voice}{!status.capabilities.tts.local && status.settings.ttsEngine === 'local' ? ' · Motore locale assente' : ''}</p>
      {view.error && <p role="alert">{view.error}</p>}
      <div style={{display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', gap: 6}}>
      <C.Button onClick={() => setTab('chat')}>Chat</C.Button>
      <C.Button onClick={() => setTab('context')}>Contesto del gioco</C.Button>
      <C.Button onClick={() => setTab('settings')}>Impostazioni e consensi</C.Button>
      </div>
      <div style={{display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: 6}}>
      <C.Button onClick={() => { void controller.stopVoice(); }}>Interrompi voce</C.Button>
      <C.Button onClick={() => { void controller.readLast(); }}>Leggi ultima risposta (massimo 1.000 caratteri)</C.Button>
      </div>
    </C.Section></div>
    <div style={{overflowY: 'auto', minHeight: 0, paddingBottom: 20}}>
    {tab === 'chat' && <Chat controller={controller} controls={C} pickImage={pickImage} />}
    {tab === 'context' && <Context controller={controller} controls={C} detectGame={detectGame} />}
    {tab === 'settings' && <SettingsPanel controller={controller} controls={C} />}
    </div>
  </div>;
}
function Chat({controller, controls: C, pickImage}: Props) {
  const {status} = useSyncExternalStore(controller.subscribe, controller.snapshot);
  const [text, setText] = useState('');
  const [image, setImage] = useState<PreparedImage>();
  const [approved, setApproved] = useState(false);
  const [busy, setBusy] = useState(false);
  const [imageError, setImageError] = useState('');
  const input = useRef<HTMLInputElement>(null);
  const end = useRef<HTMLDivElement>(null);
  const imageRef = useRef<string | undefined>(undefined);
  useEffect(() => { end.current?.scrollIntoView?.({block: 'nearest'}); }, [status?.history.length]);
  useEffect(() => { setImage(undefined); setApproved(false); imageRef.current = undefined; }, [status?.context?.revision, status?.context?.sessionId, status?.settings.imagesEnabled, status?.settings.provider, status?.settings.model]);
  useEffect(() => () => { if (imageRef.current) void controller.act('discard_image', {imageRef: imageRef.current}); }, [controller]);
  useEffect(() => {
    if (image && status?.pendingImageRef !== undefined && status.pendingImageRef !== image.imageRef) {
      setImage(undefined); setApproved(false); imageRef.current = undefined;
    }
  }, [status?.pendingImageRef, image]);
  if (!status) return null;
  const send = async (message: string) => {
    setBusy(true);
    try {
      if (await controller.send(message, image)) { setText(''); setImage(undefined); setApproved(false); imageRef.current = undefined; }
    } finally { setBusy(false); }
  };
  const selectFile = async (file?: File) => {
    if (!file || !status.context) return;
    if (!['image/png', 'image/jpeg'].includes(file.type) || file.size > 5 * 1024 * 1024) { setImageError('Scegli un PNG/JPEG fino a 5 MiB.'); return; }
    setImageError(''); setBusy(true);
    try {
      const bytes = new Uint8Array(await file.arrayBuffer());
      let binary = '';
      for (let i = 0; i < bytes.length; i += 16384) binary += String.fromCharCode(...bytes.subarray(i, i + 16384));
      const result = await controller.act<PreparedImage>('prepare_image', {dataBase64: btoa(binary), mime: file.type, sessionId: status.context.sessionId});
      setImage(result); imageRef.current = result?.imageRef; setApproved(false);
    } catch { setImageError('Immagine non leggibile.'); }
    finally { setBusy(false); if (input.current) input.current.value = ''; }
  };
  const pick = async () => {
    if (!pickImage) { input.current?.click(); return; }
    setBusy(true); setImageError('');
    try {
      const filename = await pickImage();
      if (!filename) return;
      const result = await controller.act<PreparedImage>('prepare_import_image', {filename, sessionId: status.context?.sessionId});
      setImage(result); imageRef.current = result?.imageRef; setApproved(false);
    } catch { setImageError('Scegli un PNG/JPEG nella cartella di import indicata.'); }
    finally { setBusy(false); }
  };
  return <C.Section title="Chat e suggerimenti">
    <p>Invio: titolo, AppID facoltativo, note e ultime interazioni (fino a 12 / 8.000 caratteri). Immagine solo se approvata. Le chiamate cloud possono avere costi.</p>
    <div role="log" aria-label="Cronologia" style={{maxHeight: 260, overflowY: 'auto', whiteSpace: 'pre-wrap', overflowWrap: 'anywhere'}}>
      {status.history.map((m, i) => <p key={i}><strong>{m.role === 'user' ? 'Tu' : 'DeckPilot'}: </strong>{m.content}</p>)}<div ref={end} />
    </div>
    <C.Input label="Domanda (massimo 4.000 caratteri)" value={text} onChange={setText} />
    {imageError && <p role="alert">{imageError}</p>}
    <input ref={input} type="file" accept="image/png,image/jpeg" aria-label="File immagine" style={{display: 'none'}} onChange={e => { void selectFile(e.target.files?.[0]); }} />
    <C.Button disabled={!status.settings.imagesEnabled || !status.capabilities.images || !status.context || busy} onClick={() => { void pick(); }}>Scegli immagine PNG/JPEG</C.Button>
    <p>Cattura Gaming Mode non disponibile. {pickImage ? `Copia il file nella cartella ${status.capabilities.importRoot ?? 'di import'} e sceglilo con il selettore Decky.` : 'Importa un file scelto esplicitamente.'} Focus e selettore sul dispositivo restano da verificare.</p>
    {image && <div>
      <img src={image.preview} alt="Anteprima effettiva senza metadati" style={{maxWidth: '100%', maxHeight: 200}} />
      <p>Invio a {image.destination.provider} / {image.destination.model} ({image.destination.endpoint})</p>
      <C.Button onClick={() => { void controller.act('approve_image_send', {imageRef: image.imageRef, sessionId: status.context?.sessionId, destination: image.destination}).then(value => setApproved(value !== undefined)); }}>Approva l'invio di questa immagine</C.Button>
      <C.Button onClick={() => { void controller.act('discard_image', {imageRef: image.imageRef}); setImage(undefined); imageRef.current = undefined; setApproved(false); }}>Rimuovi immagine</C.Button>
    </div>}
    <C.Button disabled={!text.trim() || text.length > 4000 || !!status.active || busy || (!!image && !approved)} onClick={() => { void send(text); }}>Chiedi</C.Button>
    <C.Button disabled={!!status.active || busy || (!!image && !approved)} onClick={() => { void send('Dammi un prossimo passo concreto; chiedi chiarimenti se manca contesto.'); }}>Suggerimento ora</C.Button>
    {status.active && <><p role="status">Richiesta in corso…</p><C.Button onClick={() => { void controller.act('cancel_request', {requestId: status.active, sessionId: status.context?.sessionId}); }}>Annulla richiesta</C.Button></>}
    <p>Al massimo un suggerimento ogni {status.settings.hintIntervalSeconds} secondi, solo con contesto nuovo e recente. Tentativi: {status.auto.attempts}/20.</p>
    <C.Toggle label="Abilita suggerimenti automatici (possibili costi)" checked={status.settings.autoHints} onChange={enabled => { void controller.act('set_auto_hints', {enabled}); }} />
    <C.Button onClick={() => { void controller.act('set_auto_hints', {paused: !status.auto.paused}); }}>{status.auto.paused ? 'Riprendi suggerimenti' : 'Pausa per questa sessione'}</C.Button>
    {status.auto.attempts >= 20 && <C.Button onClick={() => { void controller.act('set_auto_hints', {resetBudget: true, paused: false}); }}>Autorizza altri 20 tentativi</C.Button>}
    <C.Button onClick={() => { void controller.act('clear_history'); }}>Cancella cronologia di questo gioco</C.Button>
  </C.Section>;
}
function Context({controller, controls: C, detectGame}: Props) {
  const {status} = useSyncExternalStore(controller.subscribe, controller.snapshot);
  const context = status?.context;
  const [title, setTitle] = useState(context?.title ?? '');
  const [appId, setAppId] = useState(context?.appId ?? '');
  const [objective, setObjective] = useState(context?.objective ?? '');
  const [location, setLocation] = useState(context?.location ?? '');
  const [notes, setNotes] = useState(context?.userNotes ?? '');
  const save = (newSession = false) => { void controller.setContext({title, appId, objective, location, userNotes: notes, source: 'manual', newSession}); };
  const valid = validateContext(title, objective, location, notes) && (!appId || /^\d{1,20}$/.test(appId));
  const detected = detectGame?.();
  return <C.Section title="Contesto del gioco">
    <p>Il titolo da solo non rivela missione, posizione o inventario. Aggiorna obiettivo e note quando cambia il gameplay.</p>
    <C.Input label="Titolo del gioco" value={title} onChange={setTitle} />
    <C.Input label="AppID facoltativo" value={appId} onChange={setAppId} />
    <C.Input label="Obiettivo attuale" value={objective} onChange={setObjective} />
    <C.Input label="Area / posizione" value={location} onChange={setLocation} />
    <C.Input label="Note (totale contesto massimo 8.000 caratteri)" value={notes} onChange={setNotes} />
    {!valid && <p>Inserisci un titolo, AppID numerico se presente e note entro i limiti.</p>}
    <C.Button disabled={!valid} onClick={() => save()}>Salva contesto manuale</C.Button>
    <C.Button disabled={!valid} onClick={() => save(true)}>Nuova sessione per questo gioco</C.Button>
    <C.Button disabled={!detected} onClick={() => { if (detected) void controller.setContext(detected); }}>Usa gioco rilevato da Steam</C.Button>
    {!detected && <p>Rilevamento automatico non disponibile o ambiguo. Il contesto manuale funziona anche per emulatori e giochi non Steam.</p>}
  </C.Section>;
}
function SettingsPanel({controller, controls: C}: Props) {
  const {status} = useSyncExternalStore(controller.subscribe, controller.snapshot);
  const [draft, setDraft] = useState<Settings>(status!.settings);
  const [key, setKey] = useState('');
  const [saving, setSaving] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const change = <K extends keyof Settings>(field: K, value: Settings[K]) => setDraft(d => ({...d, [field]: value}));
  const changedRecipient = draft.provider !== status!.settings.provider || draft.model !== status!.settings.model || draft.ollamaEndpoint !== status!.settings.ollamaEndpoint;
  const save = async () => {
    setSaving(true);
    try {
      const patch = Object.fromEntries(Object.entries(draft).filter(([field]) => !['schemaVersion', 'configured'].includes(field)));
      const saved = await controller.updateSettings(patch);
      if (saved) setDraft(saved);
    } finally { setSaving(false); }
  };
  const saveKey = async (provider = draft.provider) => {
    setSaving(true);
    try {
      const result = await controller.act('set_api_key', {provider, key});
      if (result) setKey('');
    } finally { setSaving(false); }
  };
  return <C.Section title="Configurazione e privacy">
    <p>DeckPilot invia dati direttamente al provider scelto. Nessuna chiamata viene eseguita prima del consenso. L'abbonamento ChatGPT non include automaticamente credito API.</p>
    <C.Select label="Provider" value={draft.provider ?? ''} options={providerOptions} onChange={v => { change('provider', (v || null) as ProviderId | null); change('remoteConsent', false); change('endpointConsent', false); change('visionConfirmed', false); }} />
    <C.Input label="Modello disponibile nel tuo account" value={draft.model} onChange={v => change('model', v)} />
    {draft.provider === 'ollama' && <><C.Input label="Endpoint Ollama (localhost indica la Deck)" value={draft.ollamaEndpoint} onChange={v => change('ollamaEndpoint', v)} /><p>HTTP espone testo e immagini alla rete LAN. Usa HTTPS o un tunnel amministrato da te. Non viene configurata alcuna rete automaticamente.</p></>}
    <C.Input label="Chiave API (salvataggio separato; mai restituita)" secret value={key} onChange={setKey} />
    <p>Credenziale {draft.provider && status!.settings.configured[draft.provider] ? 'salvata; validità non verificata' : 'non salvata'}. TTS OpenAI usa una chiave OpenAI separata se la chat usa un altro provider.</p>
    <C.Button disabled={saving || !key || !draft.provider || draft.provider === 'ollama'} onClick={() => { void saveKey(); }}>Salva chiave del provider selezionato</C.Button>
    {draft.ttsEngine === 'openai' && <C.Button disabled={saving || !key} onClick={() => { void saveKey('openai'); }}>Salva chiave OpenAI per voce</C.Button>}
    <C.Button disabled={!draft.provider || draft.provider === 'ollama'} onClick={() => { setKey(''); void controller.act('delete_api_key', {provider: draft.provider}); }}>Elimina chiave del provider selezionato</C.Button>
    <C.Toggle label="Consento chat cloud: titolo, note e messaggi selezionati" checked={draft.remoteConsent} onChange={v => change('remoteConsent', v)} />
    <C.Toggle label="Autorizzo questo endpoint Ollama" checked={draft.endpointConsent} onChange={v => change('endpointConsent', v)} />
    {changedRecipient && <p>Salva prima provider/modello/endpoint, poi abilita e salva i consensi. Il cambio destinazione revoca quelli precedenti.</p>}
    <C.Toggle label="Ho verificato che questo modello supporta immagini" checked={draft.visionConfirmed} onChange={v => change('visionConfirmed', v)} />
    <C.Toggle label="Abilita import immagini; ogni invio richiede approvazione" checked={draft.imagesEnabled} onChange={v => change('imagesEnabled', v)} />
    <C.Select label="Spoiler" value={draft.spoiler} options={spoilerOptions} onChange={v => change('spoiler', v as Settings['spoiler'])} />
    <C.Input label="Durata popup in ms (2.000–15.000)" value={String(draft.popupDurationMs)} onChange={v => change('popupDurationMs', Number(v))} />
    <C.Input label="Intervallo suggerimenti in secondi (90–3.600)" value={String(draft.hintIntervalSeconds)} onChange={v => change('hintIntervalSeconds', Number(v))} />
    <C.Toggle label="Risposte vocali · voce sintetica" checked={draft.voiceEnabled} onChange={v => change('voiceEnabled', v)} />
    <C.Select label="Motore voce" value={draft.ttsEngine} options={[{value: 'local', label: 'espeak-ng locale, se presente'}, {value: 'openai', label: 'OpenAI Speech (remoto)'}]} onChange={v => change('ttsEngine', v as Settings['ttsEngine'])} />
    <C.Input label="Modello OpenAI Speech" value={draft.ttsModel} onChange={v => change('ttsModel', v)} />
    <C.Input label="Voce OpenAI Speech" value={draft.ttsVoice} onChange={v => change('ttsVoice', v)} />
    <C.Toggle label="Consento TTS OpenAI: invio del testo della risposta, possibili costi" checked={draft.ttsConsent} onChange={v => change('ttsConsent', v)} />
    <C.Input label="Volume (0–1)" value={String(draft.volume)} onChange={v => change('volume', Number(v))} />
    <C.Toggle label="Cronologia su disco (100 messaggi/gioco, 7 giorni)" checked={draft.persistentHistory} onChange={v => change('persistentHistory', v)} />
    <C.Button disabled={saving || !Number.isFinite(draft.volume) || draft.hintIntervalSeconds < 90 || draft.hintIntervalSeconds > 3600 || !Number.isInteger(draft.hintIntervalSeconds)} onClick={() => { void save(); }}>Salva impostazioni</C.Button>
    <C.Button onClick={() => { void controller.act('test_provider', {confirmCost: true}); }}>Verifica provider ora (può generare un costo)</C.Button>
    <p>Archiviazione chiavi: file privati in chiaro con permessi Linux; nessuna cifratura dichiarata. Diagnostica sanitizzata:</p>
    <pre style={{whiteSpace: 'pre-wrap', fontSize: 14}}>{JSON.stringify(status!.diagnostics, null, 2)}</pre>
    <C.Toggle label="Confermo cancellazione di cronologia, impostazioni e chiavi locali" checked={confirmDelete} onChange={setConfirmDelete} />
    <C.Button disabled={!confirmDelete} onClick={() => { setKey(''); void controller.act('delete_local_data', {confirm: true}).then(() => setDraft(controller.snapshot().status!.settings)); }}>Cancella tutti i dati locali</C.Button>
  </C.Section>;
}
