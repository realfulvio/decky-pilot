import { createRoot } from 'react-dom/client';
import { useSyncExternalStore } from 'react';
import { App } from '../components/App';
import { harnessControls } from './controls';
import { FakeBridge, fixtureStatus } from './fakeBridge';
import { Controller } from '../services/controller';
import { translate } from '../domain/i18n';
const bridge = new FakeBridge();
bridge.status.settings.provider = 'openai';
bridge.status.settings.model = 'sample-vision-model';
bridge.status.settings.configured.openai = true;
bridge.status.settings.remoteConsent = true;
bridge.status.settings.visionConfirmed = true;
bridge.status.settings.imagesEnabled = true;
bridge.status.history = [{role: 'user', content: 'The door has three symbols. Which one should I choose?', at: 0}, {role: 'assistant', content: 'I can see the blue door in your description. Look for matching symbols on the nearby wall. Share an image if you want help comparing them.', at: 0}];
const controller = new Controller(bridge, {show() {}, clear() {}}, {async play() {}, stop() {}});
await controller.start();
function Preview() {
  const view = useSyncExternalStore(controller.subscribe, controller.snapshot);
  const t = (key: Parameters<typeof translate>[1]) => translate(view.status?.settings.uiLanguage ?? 'en', key);
  return <><header><strong>DeckPilot</strong><span>{t('harnessBadge')}</span></header>
    <main><article><div className="eyebrow">DeckPilot</div><h1>{t('harnessTitle')}</h1><p>{t('harnessIntro')}</p>
      <div className="preview-orbit" aria-hidden="true">DP<span>✦</span></div>
      <div className="preview-tools"><button onClick={() => { bridge.failNext = true; }}>{t('harnessError')}</button><button onClick={() => { bridge.delay = !bridge.delay; }}>{t('harnessDelay')}</button><button onClick={() => { bridge.status = fixtureStatus(); void controller.refresh(); }}>{t('harnessOnboard')}</button></div>
    </article><aside><App controller={controller} controls={harnessControls} /></aside></main></>;
}
createRoot(document.getElementById('root')!).render(<Preview />);
