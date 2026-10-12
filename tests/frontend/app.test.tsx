import { afterEach, describe, expect, it, vi } from 'vitest';
import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { App } from '../../src/components/App';
import { harnessControls } from '../../src/harness/controls';
import { FakeBridge } from '../../src/harness/fakeBridge';
import { Controller } from '../../src/services/controller';
afterEach(cleanup);
async function setup() {
  const bridge = new FakeBridge();
  const popup = {show: vi.fn(), clear: vi.fn()};
  const audio = {play: vi.fn(), stop: vi.fn()};
  const controller = new Controller(bridge, popup, audio);
  await controller.start();
  render(<App controller={controller} controls={harnessControls} />);
  return {bridge, controller, popup, audio};
}
describe('UI italiana e flussi', () => {
  it('onboarding non invia richieste; salva e pulisce il campo chiave', async () => {
    const {bridge, controller} = await setup();
    expect(bridge.calls.every(c => c.method === 'get_status')).toBe(true);
    fireEvent.click(screen.getByText('Impostazioni e consensi'));
    fireEvent.change(screen.getByLabelText('Provider'), {target: {value: 'openai'}});
    const key = screen.getByLabelText('Chiave API (salvataggio separato; mai restituita)') as HTMLInputElement;
    fireEvent.change(key, {target: {value: 'synthetic-secret'}});
    fireEvent.click(screen.getByText('Salva chiave del provider selezionato'));
    await waitFor(() => expect(key.value).toBe(''));
    expect(JSON.stringify(controller.snapshot())).not.toContain('synthetic-secret');
    await controller.close();
  });
  it('contesto manuale senza AppID e limite 90 secondi', async () => {
    const {bridge, controller} = await setup();
    fireEvent.click(screen.getByText('Contesto del gioco'));
    fireEvent.change(screen.getByLabelText('Titolo del gioco'), {target: {value: 'Emulatore sconosciuto'}});
    fireEvent.click(screen.getByText('Salva contesto manuale'));
    await waitFor(() => expect(bridge.status.context?.title).toBe('Emulatore sconosciuto'));
    expect(bridge.status.context?.appId).toBe('');
    fireEvent.click(screen.getByText('Impostazioni e consensi'));
    fireEvent.change(screen.getByLabelText('Intervallo suggerimenti in secondi (90–3.600)'), {target: {value: '89'}});
    expect((screen.getByText('Salva impostazioni') as HTMLButtonElement).disabled).toBe(true);
    await controller.close();
  });
  it('richiesta pending annullabile e risposta completa recuperabile', async () => {
    const {bridge, controller, popup} = await setup();
    bridge.status.settings.provider = 'ollama';
    bridge.status.settings.voiceEnabled = false;
    bridge.delay = true;
    fireEvent.change(screen.getByLabelText('Domanda (massimo 4.000 caratteri)'), {target: {value: 'Dove vado?'}});
    fireEvent.click(screen.getByText('Chiedi'));
    await screen.findByText('Richiesta in corso…');
    fireEvent.click(screen.getByText('Annulla richiesta'));
    await waitFor(() => expect(bridge.status.active).toBe(null));
    bridge.delay = false;
    await act(async () => { await controller.send('Come procedo?'); });
    await screen.findByText(/Controlla il simbolo sulla porta. Se manca/);
    expect(popup.show).toHaveBeenCalledTimes(1);
    await controller.close();
  });
  it('errore provider mostrato e retry esplicito disponibile', async () => {
    const {bridge, controller} = await setup();
    bridge.failNext = true;
    await act(async () => { await controller.send('Test'); });
    expect(screen.getByRole('alert').textContent).toContain('Errore provider sintetico');
    expect(screen.getByText('Impostazioni e consensi')).toBeTruthy();
    await controller.close();
  });
  it('preview esplicita richiede approvazione prima della chat', async () => {
    const {bridge, controller} = await setup();
    bridge.status.settings.imagesEnabled = true;
    bridge.status.settings.provider = 'ollama';
    await act(async () => { await controller.refresh(); });
    const file = new File(['synthetic'], 'test.png', {type: 'image/png'});
    Object.defineProperty(file, 'arrayBuffer', {value: async () => new Uint8Array([1, 2, 3]).buffer});
    fireEvent.change(screen.getByLabelText('File immagine'), {target: {files: [file]}});
    await screen.findByAltText('Anteprima effettiva senza metadati');
    fireEvent.change(screen.getByLabelText('Domanda (massimo 4.000 caratteri)'), {target: {value: 'Cosa vedi?'}});
    expect((screen.getByText('Chiedi') as HTMLButtonElement).disabled).toBe(true);
    fireEvent.click(screen.getByText("Approva l'invio di questa immagine"));
    await waitFor(() => expect((screen.getByText('Chiedi') as HTMLButtonElement).disabled).toBe(false));
    await controller.close();
  });
});
