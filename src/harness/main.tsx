import { createRoot } from 'react-dom/client';
import { App } from '../components/App';
import { harnessControls } from './controls';
import { FakeBridge } from './fakeBridge';
import { Controller } from '../services/controller';
const bridge = new FakeBridge();
bridge.status.settings.provider = 'ollama';
bridge.status.settings.model = 'synthetic-model';
bridge.status.settings.imagesEnabled = true;
bridge.status.history = [{role: 'user', content: 'La porta ha tre simboli. Quale devo scegliere?', at: 0}, {role: 'assistant', content: 'Descrivi i simboli e le iscrizioni vicine. Con il solo titolo non posso conoscere la soluzione del puzzle.', at: 0}];
const controller = new Controller(bridge, {show() {}, clear() {}}, {async play() {}, stop() {}});
await controller.start();
createRoot(document.getElementById('root')!).render(<>
  <header><strong>DeckPilot</strong><span>HARNESS OFFLINE · risposte sintetiche, nessuna API o dispositivo</span></header>
  <main><article><h1>Un aiuto, quando serve.</h1><p>Contesto esplicito, immagini approvate e voce con consenso separato.</p><button onClick={() => { bridge.failNext = true; }}>Simula errore alla prossima domanda</button><button onClick={() => { bridge.delay = !bridge.delay; }}>Attiva/disattiva attesa per test annulla</button></article>
    <aside><App controller={controller} controls={harnessControls} /></aside>
  </main></>);
