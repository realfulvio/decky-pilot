import { useEffect, useRef, useState, useSyncExternalStore } from 'react';
import type { GameContext, PreparedImage, ProviderId, Settings } from '../domain/types';
import { translate, type Language, type MessageKey } from '../domain/i18n';
import { validateContext } from '../domain/validation';
import type { Controller } from '../services/controller';
import type { Controls } from './controls';
import { PRODUCT_NAME } from '../domain/brand';
import logo from '../../assets/brand/decky-pilot-logo-dark.png';
import menuIcon from '../../assets/brand/decky-pilot-menu.svg';

interface Props {controller: Controller; controls: Controls; detectGame?: () => Partial<GameContext> | null; pickImage?: () => Promise<string | null>; closeMenus?: () => void; openExternal?: (url: string) => void}
function useText(controller: Controller) {
  const {status} = useSyncExternalStore(controller.subscribe, controller.snapshot);
  return (key: MessageKey, values: Record<string, string | number> = {}) => translate(status?.settings.uiLanguage ?? 'en', key, values);
}
const styles = `
.dp{color:#f2f5fa;font-size:16px;line-height:1.5;overflow-wrap:anywhere}.dp p{margin:8px 0}.dp h2{font-size:19px}.dp-nav{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:5px}.dp-card{padding:12px;border:1px solid #344c61;border-radius:14px;margin:12px 0;background:linear-gradient(135deg,#17283d,#122336)}.dp-hero{background:linear-gradient(125deg,#214666,#183448);border-color:#4d889b}.dp-eyebrow{color:#88e0d0;font-size:12px;font-weight:700;letter-spacing:1.3px}.dp-game{font-size:22px;font-weight:750;line-height:1.2;margin:4px 0}.dp-subtle{color:#b9ccdb;font-size:14px}.dp-primary{border-radius:9px;background:#236b72;border:1px solid #83e1cd;padding:1px 5px;margin:12px 0}.dp-answer{border-left:3px solid #82e2cc;padding:3px 14px;white-space:pre-wrap}.dp-status{padding:8px 12px;border-radius:8px;background:#172f41}.dp section{min-width:0}.dp-scroll{max-height:68vh;overflow-y:auto;padding:0 2px 18px}.dp img{max-width:100%;max-height:180px;border-radius:10px}.dp button:focus-visible{outline:3px solid #a1f4df;outline-offset:3px}.dp-actions{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:5px}
`;
export function App(props: Props) {
  const {controller, controls: C} = props;
  const view = useSyncExternalStore(controller.subscribe, controller.snapshot);
  const t = useText(controller);
  const [tab, setTab] = useState<'chat' | 'context' | 'settings'>('chat');
  const [wizard, setWizard] = useState<number | null>(null);
  const language = view.status?.settings.uiLanguage ?? 'en';
  useEffect(() => { document.documentElement.lang = language; }, [language]);
  useEffect(() => { void controller.bridge.rpc('set_capture_guard', {blocked: tab !== 'chat' || wizard !== null}).catch(() => undefined); }, [controller, tab, wizard]);
  if (!view.status) return <C.Section title={PRODUCT_NAME}><p>{t('loading')}</p>{view.error && <p role="alert">{t(view.error)}</p>}<C.Button onClick={() => { void controller.refresh(); }}>{t('retry')}</C.Button></C.Section>;
  const status = view.status;
  const configured = !!status.settings.provider && !!status.settings.model && (status.settings.provider === 'ollama' || status.settings.configured[status.settings.provider]);
  const consent = status.settings.provider === 'ollama' ? status.settings.endpointConsent : status.settings.remoteConsent;
  return <C.Group className="dp"><style>{styles}</style>
    <div style={{display:"flex", alignItems:"center", gap:8, marginBottom:8}}><img src={menuIcon} alt="" width={24} height={24} /><strong>{PRODUCT_NAME}</strong></div>
    <C.Group className="dp-nav" direction="horizontal">
      <C.Button onClick={() => { setWizard(null); setTab('chat'); }}>{t('home')}</C.Button>
      <C.Button onClick={() => { setWizard(null); setTab('context'); }}>{t('context')}</C.Button>
      <C.Button onClick={() => { setWizard(null); setTab('settings'); }}>{t('settings')}</C.Button>
    </C.Group>
    {view.error && <p className="dp-status" role="alert">{t(view.error)}</p>}
    <div className="dp-scroll">
      {wizard !== null ? <div className="dp-card">
        <C.Section title={t((['stepGame', 'stepProvider', 'stepConsent'] as const)[wizard])}>
          {wizard === 0 ? <Context {...props} /> : <SettingsPanel {...props} mode={wizard === 1 ? 'provider' : 'sharing'} />}
          <div className="dp-actions"><C.Button onClick={() => setWizard(wizard === 0 ? null : wizard - 1)}>{t('back')}</C.Button>
          <C.Button disabled={wizard === 0 ? !status.context : wizard === 1 ? !configured : !configured || !consent} onClick={() => setWizard(wizard === 2 ? null : wizard + 1)}>{t(wizard === 2 ? 'finish' : 'next')}</C.Button></div>
        </C.Section>
      </div> : tab === 'chat' ? <>
        <div className="dp-card dp-hero"><div className="dp-eyebrow">{t('activeGame')}</div>
          <div className="dp-game">{status.context?.title || t('setGame')}</div>
          <p className="dp-subtle">{t(configured && consent ? 'ready' : 'needsSetup')}</p>
        </div>
        {(!configured || !consent) && <div className="dp-card"><img src={logo} alt={PRODUCT_NAME} width={210} style={{display:'block',maxWidth:'100%',height:'auto',margin:'0 auto 8px'}} /><C.Section title={t('onboardTitle')}><p>{t('onboardIntro')}</p><C.Button onClick={() => setWizard(0)}>{t('getStarted')}</C.Button></C.Section></div>}
        <Chat {...props} ready={configured && consent} />
      </> : tab === 'context' ? <Context {...props} /> : <SettingsPanel {...props} mode="full" />}
    </div>
  </C.Group>;
}
function Chat({controller, controls: C, pickImage, closeMenus, ready}: Props & {ready: boolean}) {
  const view = useSyncExternalStore(controller.subscribe, controller.snapshot);
  const status = view.status!;
  const t = useText(controller);
  const [text, setText] = useState('');
  const [image, setImage] = useState<PreparedImage>();
  const [approved, setApproved] = useState(false);
  const [busy, setBusy] = useState(false);
  const [imageError, setImageError] = useState<MessageKey | ''>('');
  const [showHistory, setShowHistory] = useState(false);
  const [autoInfo, setAutoInfo] = useState(false);
  const [captureDialog, setCaptureDialog] = useState(false);
  const [confirmCapture, setConfirmCapture] = useState(false);
  const input = useRef<HTMLInputElement>(null);
  const imageRef = useRef<string | undefined>(undefined);
  const latest = [...status.history].reverse().find(message => message.role === 'assistant');
  const latestResult = [...status.requests].reverse().find(record => record.state === 'completed')?.result;
  const readable = !!latest && status.requests.some(record => record.state === 'completed' && record.sessionId === status.context?.sessionId && record.contextRevision === status.context?.revision);
  useEffect(() => { setImage(undefined); setApproved(false); imageRef.current = undefined; }, [status.context?.revision, status.context?.sessionId, status.settings.imagesEnabled, status.settings.provider, status.settings.model]);
  useEffect(() => () => { if (imageRef.current) void controller.act('discard_image', {imageRef: imageRef.current}); }, [controller]);
  useEffect(() => {
    if (image && status.pendingImageRef !== undefined && status.pendingImageRef !== image.imageRef) {
      setImage(undefined); setApproved(false); imageRef.current = undefined;
    }
  }, [status.pendingImageRef, image]);
  const prepared = (value?: PreparedImage) => { setImage(value); imageRef.current = value?.imageRef; setApproved(false); };
  const send = async (help = false) => {
    setBusy(true);
    try { if (await (help ? controller.helpNow(image, text) : controller.send(text, image))) { setText(''); prepared(); } }
    finally { setBusy(false); }
  };
  const pick = async () => {
    if (!pickImage) { input.current?.click(); return; }
    setBusy(true); setImageError('');
    try {
      const filename = await pickImage();
      if (filename) prepared(await controller.act<PreparedImage>('prepare_import_image', {filename, sessionId: status.context?.sessionId}));
    } catch { setImageError('imageUnreadable'); }
    finally { setBusy(false); }
  };
  const selectFile = async (file?: File) => {
    if (!file || !status.context) return;
    if (!['image/png', 'image/jpeg'].includes(file.type) || file.size > 5 * 1024 * 1024) { setImageError('imageLimit'); return; }
    setImageError(''); setBusy(true);
    try {
      const bytes = new Uint8Array(await file.arrayBuffer()); let binary = '';
      for (let i = 0; i < bytes.length; i += 16384) binary += String.fromCharCode(...bytes.subarray(i, i + 16384));
      prepared(await controller.act<PreparedImage>('prepare_image', {dataBase64: btoa(binary), mime: file.type, sessionId: status.context.sessionId}));
    } catch { setImageError('imageUnreadable'); }
    finally { setBusy(false); if (input.current) input.current.value = ''; }
  };
  const capture = async () => {
    setBusy(true);
    try {
      closeMenus?.();
      await new Promise(resolve => setTimeout(resolve, 700));
      prepared(await controller.act<PreparedImage>('prepare_capture', {sessionId: status.context?.sessionId, confirmGameplay: confirmCapture}));
    } finally { setBusy(false); setConfirmCapture(false); setCaptureDialog(false); }
  };
  const disabled = !ready || !status.context || !!status.active || busy || (!!image && !approved);
  return <>
    <div className="dp-primary"><C.Button disabled={disabled} onClick={() => {
      if (!image && status.capabilities.capture && status.settings.captureEnabled) setCaptureDialog(true);
      else if (!image && status.settings.imagesEnabled) void pick();
      else void send(true);
    }}>{t('helpNow')}</C.Button></div>
    {!status.capabilities.capture && <p className="dp-subtle">{t('captureUnavailable')}</p>}
    {captureDialog && <div className="dp-card"><p>{t('captureConsent')}</p><C.Toggle label={t('captureConfirm')} checked={confirmCapture} onChange={setConfirmCapture} />
      <C.Button disabled={!confirmCapture || busy} onClick={() => { void capture(); }}>{t('captureAction')}</C.Button></div>}
    {imageError && <p role="alert">{t(imageError)}</p>}
    {image && <div className="dp-card"><img src={image.preview} alt={t('imagePreview')} /><p>{t('imageDestination', image.destination)}</p><p className="dp-subtle">{t('imageSafety')}</p>
      <C.Button onClick={() => { void controller.act('approve_image_send', {imageRef: image.imageRef, sessionId: status.context?.sessionId, destination: image.destination}).then(value => setApproved(value !== undefined)); }}>{t('approveImage')}</C.Button>
      <C.Button onClick={() => { void controller.act('discard_image', {imageRef: image.imageRef}); prepared(); }}>{t('removeImage')}</C.Button>
    </div>}
    <C.Input label={t('question')} value={text} onChange={setText} />
    <div className="dp-actions"><C.Button disabled={disabled || !text.trim() || text.length > 4000} onClick={() => { void send(); }}>{t('ask')}</C.Button>
      <C.Button disabled={!status.settings.imagesEnabled || !status.capabilities.images || !status.context || busy} onClick={() => { void pick(); }}>{t('importImage')}</C.Button></div>
    <input ref={input} type="file" accept="image/png,image/jpeg" aria-label={t('imageFile')} style={{display: 'none'}} onChange={e => { void selectFile(e.target.files?.[0]); }} />
    {status.active && <div className="dp-status"><p role="status">{t('pending')}</p><C.Button onClick={() => { void controller.act('cancel_request', {requestId: status.active, sessionId: status.context?.sessionId}); }}>{t('cancel')}</C.Button></div>}
    <div className="dp-card"><C.Section title={t(latestResult?.situation?.clarification ? 'clarificationTitle' : 'latestAnswer')}><p className="dp-answer">{latest?.content ?? t('emptyAnswer')}</p>
      <p className="dp-subtle">{t(view.voice)}</p><div className="dp-actions"><C.Button disabled={!readable} onClick={() => { void controller.readLast(); }}>{t('readLast')}</C.Button><C.Button onClick={() => { void controller.stopVoice(); }}>{t('stopVoice')}</C.Button></div>
    </C.Section></div>
    <div className="dp-status"><p role="status">{t(status.settings.autoHints && status.auto.sessionConsent ? status.auto.paused ? 'autoPaused' : 'autoActive' : 'autoOff')}</p>
      {status.settings.autoHints && status.auto.sessionConsent && <><C.Button onClick={() => { void controller.act('set_auto_hints', {paused: true}); }}>{t('pauseAuto')}</C.Button><p className="dp-subtle">{t('autoLimit', {seconds: status.settings.hintIntervalSeconds, attempts: status.auto.attempts})}</p></>}
      {status.capabilities.capture ? <C.Toggle label={t('autoConsent')} checked={status.settings.autoHints && !!status.auto.sessionConsent && !status.auto.paused} onChange={enabled => { void controller.act('set_auto_hints', {enabled, paused: !enabled, consent: enabled, visual: true, sessionId: status.context?.sessionId}); }} /> : <><C.Button onClick={() => setAutoInfo(!autoInfo)}>{t('autoTitle')}</C.Button>{autoInfo && <p className="dp-subtle">{t('autoUnavailable')}</p>}</>}
      {status.auto.attempts >= 20 && <C.Button onClick={() => { void controller.act('set_auto_hints', {resetBudget: true, paused: false, enabled: true, consent: true, visual: true, sessionId: status.context?.sessionId}); }}>{t('allowMore')}</C.Button>}
    </div>
    <C.Button onClick={() => setShowHistory(!showHistory)}>{t('showHistory')}</C.Button>
    {showHistory && <div role="log" aria-label={t('history')}>{status.history.map((message, i) => <p key={i}><strong>{message.role === 'user' ? t('you') : PRODUCT_NAME}: </strong>{message.content}</p>)}<C.Button onClick={() => { void controller.act('clear_history'); }}>{t('clearHistory')}</C.Button></div>}
  </>;
}
function Context({controller, controls: C, detectGame}: Props) {
  const {status} = useSyncExternalStore(controller.subscribe, controller.snapshot);
  const t = useText(controller); const context = status?.context;
  const [title, setTitle] = useState(context?.title ?? ''); const [appId, setAppId] = useState(context?.appId ?? '');
  const [objective, setObjective] = useState(context?.objective ?? ''); const [location, setLocation] = useState(context?.location ?? ''); const [notes, setNotes] = useState(context?.userNotes ?? '');
  const [advanced, setAdvanced] = useState(false);
  useEffect(() => {
    setTitle(context?.title ?? ''); setAppId(context?.appId ?? '');
    setObjective(context?.objective ?? ''); setLocation(context?.location ?? ''); setNotes(context?.userNotes ?? '');
  }, [context?.sessionId, context?.revision, context?.title, context?.appId, context?.objective, context?.location, context?.userNotes]);
  const valid = validateContext(title, objective, location, notes) && (!appId || /^\d{1,20}$/.test(appId)); const detected = detectGame?.();
  return <C.Section title={t('context')}><p className="dp-subtle">{t('gameIntro')}</p>
    <C.Input label={t('gameTitle')} value={title} onChange={setTitle} /><C.Input label={t('objective')} value={objective} onChange={setObjective} />
    <C.Button onClick={() => setAdvanced(!advanced)}>{t('advanced')}</C.Button>{advanced && <><C.Input label={t('location')} value={location} onChange={setLocation} /><C.Input label={t('notes')} value={notes} onChange={setNotes} /><C.Input label={t('appId')} value={appId} onChange={setAppId} /></>}
    {!valid && <p role="alert">{t('invalidContext')}</p>}
    <C.Button disabled={!valid} onClick={() => { void controller.setContext({title, appId, objective, location, userNotes: notes, source: 'manual'}); }}>{t('saveContext')}</C.Button>
    <C.Button disabled={!valid} onClick={() => { void controller.setContext({title, appId, objective, location, userNotes: notes, source: 'manual', newSession: true}); }}>{t('newSession')}</C.Button>
    <C.Button disabled={!detected} onClick={() => { if (detected) void controller.setContext(detected); }}>{t('useSteam')}</C.Button>{!detected && <p className="dp-subtle">{t('noSteam')}</p>}
  </C.Section>;
}
function SettingsPanel({controller, controls: C, mode, openExternal}: Props & {mode: 'provider' | 'sharing' | 'full'}) {
  const {status} = useSyncExternalStore(controller.subscribe, controller.snapshot); const t = useText(controller);
  const [draft, setDraft] = useState<Settings>(status!.settings); const [key, setKey] = useState(''); const [speechKey, setSpeechKey] = useState(''); const [saving, setSaving] = useState(false); const [advanced, setAdvanced] = useState(false); const [confirmDelete, setConfirmDelete] = useState(false);
  const change = <K extends keyof Settings>(field: K, value: Settings[K]) => setDraft(d => ({...d, [field]: value}));
  const languages = [{value: 'en', label: t('english')}, {value: 'it', label: t('italian')}];
  const [models, setModels] = useState<{id: string; label: string; images: boolean}[]>([]);
  const [partial, setPartial] = useState(false);
  const [account, setAccount] = useState(status?.chatgpt?.active ?? '');
  useEffect(() => {setAccount(status?.chatgpt?.active ?? '');}, [status?.chatgpt?.active]);
  useEffect(() => {setModels([]);setPartial(false);}, [draft.provider, status?.chatgpt?.active, status?.chatgpt?.connected]);
  useEffect(() => {if(draft.provider) setModels(status?.catalogs?.[draft.provider] ?? []);}, [draft.provider,status?.catalogs]);
  const loadModels = async () => {
    setSaving(true);
    try { const result = await controller.act<{models: typeof models; partial: boolean}>('list_models', {provider: draft.provider, consent: true});
      if (result) {setModels(result.models);setPartial(result.partial);} } finally {setSaving(false);}
  };
  const signIn = async () => {
    try {
      const result = await controller.act<{authorizationUrl: string}>('begin_chatgpt_sign_in', account ? {accountId: account} : {});
      if (result) {if(openExternal) openExternal(result.authorizationUrl); else window.open(result.authorizationUrl, '_blank', 'noopener,noreferrer');}
    } catch { await controller.act('cancel_chatgpt_sign_in'); }
  };
  const changedRecipient = draft.provider !== status!.settings.provider || draft.model !== status!.settings.model || draft.ollamaEndpoint !== status!.settings.ollamaEndpoint;
  const save = async () => { setSaving(true); try { const saved = await controller.updateSettings(Object.fromEntries(Object.entries(draft).filter(([field]) => !['schemaVersion', 'configured'].includes(field)))); if (saved) setDraft(saved); } finally { setSaving(false); } };
  const saveKey = async (speech = false) => { setSaving(true); try { if (await controller.act('set_api_key', {provider:speech ? 'openai' : draft.provider, key:speech ? speechKey : key})) {if(speech) setSpeechKey(''); else setKey('');} } finally { setSaving(false); } };
  return <C.Section title={t(mode === 'sharing' ? 'sharing' : 'settings')}>
    {mode === 'full' && <><C.Select label={t('uiLanguage')} value={draft.uiLanguage} options={languages} onChange={v => { change('uiLanguage', v as Language); void controller.updateSettings({uiLanguage: v as Language}); }} />
      <C.Select label={t('responseLanguage')} value={draft.responseLanguage} options={languages} onChange={v => change('responseLanguage', v as Language)} />
      <p className="dp-subtle">{t('languageNote')}</p></>}
    {mode !== 'sharing' && <><p>{t('providerIntro')}</p>
      <C.Select label={t('provider')} value={draft.provider ?? ''} options={[{value: '', label: t('noneProvider')}, {value:'chatgpt',label:'ChatGPT'}, {value:'openai',label:t('openaiAdvanced')}, ...['Claude','Gemini','Grok','Ollama'].map(name => ({value: name.toLowerCase(), label: name}))]} onChange={v => { setKey(''); change('provider', (v || null) as ProviderId | null); change('model',''); change('remoteConsent', false); change('endpointConsent', false); change('visionConfirmed', false); }} />
      {draft.provider === 'ollama' && <C.Input label={t('model')} value={draft.model} onChange={v => change('model',v)} />}
      <C.Select label={t(draft.provider === 'ollama' ? 'catalogModel' : 'model')} value={draft.model} options={[{value:'',label:t('chooseModel')}, ...models.map(model => ({value:model.id,label:model.label + (model.images ? ` · ${t('visionReady')}` : ` · ${t('visionUnknown')}`)})), ...(!models.some(model => model.id === draft.model) && draft.model ? [{value:draft.model,label:draft.model}] : [])]} onChange={v => {change('model',v);change('remoteConsent',false);change('visionConfirmed',false);}} />
      <C.Button disabled={saving || !draft.provider} onClick={() => {void loadModels();}}>{t('loadModels')}</C.Button>
      <p className="dp-subtle">{t('catalogConsent')}</p>{partial && <p>{t('catalogPartial')}</p>}
      <p className="dp-subtle">{t('modelAvailability')}</p>
      {draft.provider === 'chatgpt' ? <div className="dp-card"><p>{t('chatgptPlan')}</p>
        {status?.chatgpt?.active && <p>{t('activeChatGPT',{account:status.chatgpt.accounts.find(value => value.id === status.chatgpt?.active)?.label ?? 'ChatGPT'})}</p>}
        <C.Select label={t('chatgptAccount')} value={account} options={[{value:'',label:t('newAccount')}, ...(status?.chatgpt?.accounts ?? []).map(value => ({value:value.id,label:`${value.label} · ${value.registration}`}))]} onChange={setAccount} />
        <C.Button onClick={() => {void signIn();}}>{t('continueChatGPT')}</C.Button>
        <p role="status">{t(status?.chatgpt?.connected ? 'accountConnected' : 'accountDisconnected')}</p>
        <p className="dp-subtle">{t('chatgptHardware')}</p>
        {status?.chatgpt?.state === 'pending' && <C.Button onClick={() => {void controller.act('cancel_chatgpt_sign_in');}}>{t('cancelSignIn')}</C.Button>}
        {status?.chatgpt?.error && <p role="alert">{translate(draft.uiLanguage, ('error.' + status.chatgpt.error) as MessageKey)}</p>}
        {status?.catalogError && <p role="alert">{translate(draft.uiLanguage, ('error.' + status.catalogError) as MessageKey)}</p>}
        <C.Button onClick={() => {void controller.act('disconnect_chatgpt');}}>{t('disconnectAccount')}</C.Button>
        <a href="https://chatgpt.com/settings/usage" target="_blank" rel="noreferrer">{t('planUsage')}</a>
      </div> : draft.provider === 'ollama' ? <><C.Input label={t('ollamaEndpoint')} value={draft.ollamaEndpoint} onChange={v => change('ollamaEndpoint', v)} /><p className="dp-subtle">{t('httpPrivacy')}</p></> : <><p className="dp-subtle">{t('apiBilling')}</p><C.Input label={t('apiKey')} secret value={key} onChange={setKey} />
        <p className="dp-subtle">{t(draft.provider && status!.settings.configured[draft.provider] ? 'keySaved' : 'keyMissing')}</p>
        <div className="dp-actions"><C.Button disabled={saving || !key || !draft.provider} onClick={() => { void saveKey(); }}>{t('saveKey')}</C.Button><C.Button disabled={!draft.provider} onClick={() => { setKey(''); void controller.act('delete_api_key', {provider: draft.provider}); }}>{t('deleteKey')}</C.Button></div></>}
    </>}
    {mode !== 'provider' && <>
      <C.Toggle label={t(draft.provider === 'ollama' ? 'endpointConsent' : 'chatConsent')} checked={draft.provider === 'ollama' ? draft.endpointConsent : draft.remoteConsent} onChange={v => change(draft.provider === 'ollama' ? 'endpointConsent' : 'remoteConsent', v)} />
      {changedRecipient && <p>{t('recipientChanged')}</p>}
      <C.Toggle label={t('visionConfirmed')} checked={draft.visionConfirmed} onChange={v => change('visionConfirmed', v)} />
      <C.Toggle label={t('imagesEnabled')} checked={draft.imagesEnabled} onChange={v => change('imagesEnabled', v)} />
      {status!.capabilities.capture && <C.Toggle label={t('captureEnabled')} checked={draft.captureEnabled} onChange={v => change('captureEnabled', v)} />}
      {!status!.capabilities.capture && <p className="dp-subtle">{t('captureUnavailable')}</p>}
    </>}
    {mode === 'full' && <>
      <C.Select label={t('spoilers')} value={draft.spoiler} options={[{value: 'none', label: t('spoilerNone')}, {value: 'hints', label: t('spoilerHints')}, {value: 'full_solutions', label: t('spoilerFull')}]} onChange={v => change('spoiler', v as Settings['spoiler'])} />
      <C.Toggle label={t('voiceEnabled')} checked={draft.voiceEnabled} onChange={v => change('voiceEnabled', v)} />
      <C.Select label={t('voiceEngine')} value={draft.ttsEngine} options={[{value: 'local', label: t('localVoice')}, {value: 'openai', label: t('remoteVoice')}]} onChange={v => change('ttsEngine', v as Settings['ttsEngine'])} />
      {draft.ttsEngine === 'openai' && <><C.Input label={t('speechVoice')} value={draft.ttsVoice} onChange={v => change('ttsVoice', v)} /><C.Input label={t('speechKey')} secret value={speechKey} onChange={setSpeechKey} /><C.Button disabled={saving || !speechKey} onClick={() => { void saveKey(true); }}>{t('saveSpeechKey')}</C.Button><C.Toggle label={t('speechConsent')} checked={draft.ttsConsent} onChange={v => change('ttsConsent', v)} /></>}
      <C.Input label={t('volume')} value={String(draft.volume)} onChange={v => change('volume', Number(v))} />
      <C.Button onClick={() => setAdvanced(!advanced)}>{t('advanced')}</C.Button>
      {advanced && <><C.Input label={t('popupDuration')} value={String(draft.popupDurationMs)} onChange={v => change('popupDurationMs', Number(v))} /><C.Input label={t('hintInterval')} value={String(draft.hintIntervalSeconds)} onChange={v => change('hintIntervalSeconds', Number(v))} /><C.Toggle label={t('persistHistory')} checked={draft.persistentHistory} onChange={v => change('persistentHistory', v)} />
        <p className="dp-subtle">{t('storagePrivacy')}</p>{status!.capabilities.importRoot && <p className="dp-subtle">{t('importHint', {folder: status!.capabilities.importRoot})}</p>}
        <C.Button onClick={() => { void controller.act('test_provider', {confirmCost: true}); }}>{t('checkProvider')}</C.Button><C.Toggle label={t('confirmDelete')} checked={confirmDelete} onChange={setConfirmDelete} /><C.Button disabled={!confirmDelete} onClick={() => { setKey(''); setSpeechKey(''); void controller.act('delete_local_data', {confirm: true}).then(() => setDraft(controller.snapshot().status!.settings)); }}>{t('deleteData')}</C.Button>
      </>}
    </>}
    <C.Button disabled={saving || !Number.isFinite(draft.volume) || draft.hintIntervalSeconds < 90 || draft.hintIntervalSeconds > 3600 || !Number.isInteger(draft.hintIntervalSeconds)} onClick={() => { void save(); }}>{t('saveSettings')}</C.Button>
    {mode === 'sharing' && <C.Button disabled={!status!.settings.provider || !(status!.settings.provider === 'ollama' ? status!.settings.endpointConsent : status!.settings.remoteConsent)} onClick={() => {void controller.act('test_provider',{confirmCost:true});}}>{t('checkProvider')}</C.Button>}
  </C.Section>;
}
