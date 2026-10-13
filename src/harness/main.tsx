import { createRoot } from 'react-dom/client';
import { useState, useSyncExternalStore } from 'react';
import { App } from '../components/App';
import { harnessControls } from './controls';
import { FakeBridge, fixtureStatus } from './fakeBridge';
import { Controller } from '../services/controller';
import { translate } from '../domain/i18n';
import { PRODUCT_NAME } from '../domain/brand';
import logo from '../../assets/brand/decky-pilot-logo-dark.png';
import fixture from '../../tests/fixtures/contract.json';
import type {AssistantResult} from '../domain/types';
const bridge = new FakeBridge();
bridge.status.settings.provider = 'openai';
bridge.status.settings.model = 'gpt-4.1-2025-04-14';
bridge.status.settings.configured.openai = true;
bridge.status.settings.remoteConsent = true;
bridge.status.settings.visionConfirmed = true;
bridge.status.settings.imagesEnabled = true;
const syntheticAnswer = 'Visible (synthetic scene):\nA door with three symbols and a lever.\n\nPossible explanation:\nThe lever may respond to the matching symbol.\n\nNext steps:\n1. Compare the door symbols with the nearby markings.\n2. Try the matching symbol, then the lever.\n\nThis is a simulated response, not live AI analysis.';
const previewAnswer = (answer: string) => {
  bridge.status.history = [{role:'user',content:'How do I open the door?',at:0},{role:'assistant',content:answer,at:0}];
  bridge.status.requests = [{requestId:fixture.result.requestId,sessionId:bridge.status.context!.sessionId,contextRevision:bridge.status.context!.revision,kind:'manual',state:'completed',result:{...fixture.result,answer,sessionId:bridge.status.context!.sessionId,contextRevision:bridge.status.context!.revision} as AssistantResult}];
  if (answer.includes('Which objective are you trying to complete?')) bridge.status.requests[0].result!.situation = {
    observations:['A door with three symbols (synthetic scene).'],inferences:['The route is unclear.'],goal:'',obstacle:'',steps:[],
    clarification:'Which objective are you trying to complete?',phase:'unknown',useful:true};
};
previewAnswer(syntheticAnswer);
const controller = new Controller(bridge, {show() {}, clear() {}}, {async play() {}, stop() {}});
await controller.start();
// ?picker=1 mimics Decky: the plugin panel is removed from the document while a modal file picker is open.
// ?qam=1 renders the panel in a narrow Quick Access-like column.
const query = new URLSearchParams(location.search);
let finishPick: ((name: string | null) => void) | undefined;
function Preview() {
  const [pickerOpen, setPickerOpen] = useState(false);
  const pickImage = query.has('picker') ? () => new Promise<string | null>(resolve => {
    finishPick = name => { setPickerOpen(false); resolve(name); };
    setPickerOpen(true);
  }) : undefined;
  const view = useSyncExternalStore(controller.subscribe, controller.snapshot);
  const t = (key: Parameters<typeof translate>[1]) => translate(view.status?.settings.uiLanguage ?? 'en', key);
  return <><header><strong>{PRODUCT_NAME}</strong><span>{t('harnessBadge')}</span></header>
    <main><article><div className="eyebrow">{PRODUCT_NAME}</div><h1>{t('harnessTitle')}</h1><p>{t('harnessIntro')}</p>
      <img src={logo} alt={PRODUCT_NAME} width={350} style={{maxWidth:'100%',height:'auto',borderRadius:12,marginTop:24}} />
      <div className="preview-tools"><button onClick={() => { bridge.failNext = true; }}>{t('harnessError')}</button><button onClick={() => { bridge.delay = !bridge.delay; }}>{t('harnessDelay')}</button><button onClick={() => { bridge.status = fixtureStatus(); void controller.refresh(); }}>{t('harnessOnboard')}</button>
        <button onClick={() => {bridge.status.settings.provider='chatgpt';bridge.status.settings.model='';bridge.status.chatgpt={state:'idle',connected:false,active:null,accounts:[]};void controller.refresh();}}>Preview ChatGPT setup</button>
        <button onClick={() => {previewAnswer('Visible (synthetic scene):\nA door with three symbols.\n\nPossible explanation:\nThe route is unclear.\n\nWhich objective are you trying to complete?\n\nSimulated clarification; no live model.');void controller.refresh();}}>Preview clarification</button>
        <button onClick={() => {bridge.status.capabilities.capture=true;bridge.status.settings.captureEnabled=true;void controller.refresh();}}>Preview capture controls (simulated)</button>
      </div>
    </article>{pickerOpen && <div role="dialog" aria-label="Simulated file picker" style={{padding:16}}><p>deckpilot-synthetic-test.png</p><button onClick={() => finishPick?.('deckpilot-synthetic-test.png')}>Select this file</button></div>}
      {!pickerOpen && <aside className={query.has('qam') ? 'qam' : undefined}><App openExternal={() => { /* Offline harness never opens a real sign-in. */ }} pickImage={pickImage} controller={controller} controls={harnessControls} /></aside>}</main></>;
}
createRoot(document.getElementById('root')!).render(<Preview />);
