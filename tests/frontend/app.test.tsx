import { afterEach, describe, expect, it, vi } from 'vitest';
import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { App } from '../../src/components/App';
import { harnessControls } from '../../src/harness/controls';
import { FakeBridge } from '../../src/harness/fakeBridge';
import { Controller } from '../../src/services/controller';
import { translate } from '../../src/domain/i18n';
import en from '../../locales/en.json';
import itCatalog from '../../locales/it.json';
afterEach(cleanup);
async function setup(ready = false) {
  const bridge = new FakeBridge();
  if (ready) Object.assign(bridge.status.settings, {provider: 'openai', model: 'sample', configured: {openai: true}, remoteConsent: true, imagesEnabled: true, visionConfirmed: true});
  const popup = {show: vi.fn(), clear: vi.fn()}; const audio = {play: vi.fn(), stop: vi.fn()};
  const controller = new Controller(bridge, popup, audio); await controller.start();
  render(<App controller={controller} controls={harnessControls} />);
  return {bridge, controller, popup, audio};
}
describe('English-first UI and complete Italian localization', () => {
  it('has identical catalog keys and interpolation fields', () => {
    expect(Object.keys(itCatalog).sort()).toEqual(Object.keys(en).sort());
    for (const key of Object.keys(en) as (keyof typeof en)[]) {
      expect(itCatalog[key].match(/\{\w+\}/g)?.sort()).toEqual(en[key].match(/\{\w+\}/g)?.sort());
      expect(itCatalog[key].trim()).not.toBe('');
    }
    expect(translate('it', 'helpNow')).toBe('Aiutami ora');
  });
  it('onboarding is English, sends no AI requests and clears the saved key', async () => {
    const {bridge, controller} = await setup();
    expect(screen.getByText('Let’s get you unstuck')).toBeTruthy();
    expect(bridge.calls.every(c => ['get_status', 'set_capture_guard'].includes(c.method))).toBe(true);
    fireEvent.click(screen.getByRole('button', {name: 'Settings'}));
    fireEvent.change(screen.getByLabelText('AI service'), {target: {value: 'openai'}});
    const key = screen.getByLabelText('API key') as HTMLInputElement;
    fireEvent.change(key, {target: {value: 'synthetic-secret'}});
    fireEvent.click(screen.getByText('Save key'));
    await waitFor(() => expect(key.value).toBe(''));
    expect(JSON.stringify(controller.snapshot())).not.toContain('synthetic-secret');
    expect(bridge.calls.some(c => ['start_assistant_request','test_provider','start_tts'].includes(c.method))).toBe(false);
    await controller.close();
  });
  it('guides setup through game, service and permissions without sending a generation', async () => {
    const {bridge, controller} = await setup();
    fireEvent.click(screen.getByText('Get started'));
    expect(screen.getByText('1 · Your game')).toBeTruthy();
    fireEvent.click(screen.getByText('Next'));
    expect(screen.getByText('2 · Your AI service')).toBeTruthy();
    expect((screen.getByText('Next') as HTMLButtonElement).disabled).toBe(true);
    fireEvent.change(screen.getByLabelText('AI service'), {target: {value: 'ollama'}});
    fireEvent.change(screen.getByLabelText('Model available in your account'), {target: {value: 'test-model'}});
    fireEvent.click(screen.getByText('Save settings'));
    await waitFor(() => expect((screen.getByText('Next') as HTMLButtonElement).disabled).toBe(false));
    fireEvent.click(screen.getByText('Next'));
    expect(screen.getByText('3 · Your choice')).toBeTruthy();
    expect((screen.getByText('Ready to play') as HTMLButtonElement).disabled).toBe(true);
    expect(bridge.calls.some(c => c.method === 'start_assistant_request')).toBe(false);
    await controller.close();
  });
  it('switches the whole UI without changing AI or voice language', async () => {
    const {bridge, controller} = await setup();
    fireEvent.click(screen.getByRole('button', {name: 'Settings'}));
    fireEvent.change(screen.getByLabelText('Interface language'), {target: {value: 'it'}});
    await screen.findByText('Lingua dell’interfaccia');
    expect(bridge.status.settings.responseLanguage).toBe('en');
    expect(bridge.status.settings.ttsLanguage).toBe('en');
    fireEvent.change(screen.getByLabelText('Lingua delle risposte AI'), {target: {value: 'it'}});
    fireEvent.click(screen.getByText('Salva impostazioni'));
    await waitFor(() => expect(bridge.status.settings.responseLanguage).toBe('it'));
    expect(bridge.status.settings.ttsLanguage).toBe('en');
    expect(document.documentElement.lang).toBe('it');
    await controller.close();
  });
  it('keeps technical details off Play and validates the automatic interval in Settings', async () => {
    const {bridge, controller} = await setup();
    expect(screen.queryByText(/diagnostic/i)).toBe(null);
    expect(screen.queryByLabelText('API key')).toBe(null);
    fireEvent.click(screen.getByRole('button', {name: 'Game'}));
    fireEvent.change(screen.getByLabelText('Game title'), {target: {value: 'Unknown emulator'}});
    fireEvent.click(screen.getByText('Save game'));
    await waitFor(() => expect(bridge.status.context?.title).toBe('Unknown emulator'));
    expect(bridge.status.context?.appId).toBe('');
    fireEvent.click(screen.getByRole('button', {name: 'Settings'}));
    fireEvent.click(screen.getByText('Advanced options'));
    fireEvent.change(screen.getByLabelText('Automatic interval, seconds (90–3,600)'), {target: {value: '89'}});
    expect((screen.getByText('Save settings') as HTMLButtonElement).disabled).toBe(true);
    await waitFor(() => expect(bridge.calls.some(c => c.method === 'set_capture_guard' && c.payload.blocked === true)).toBe(true));
    await controller.close();
  });
  it('shows pending state, cancellation and the full latest answer', async () => {
    const {bridge, controller, popup} = await setup(true);
    bridge.status.settings.voiceEnabled = false; bridge.delay = true;
    fireEvent.change(screen.getByLabelText('Or ask a question'), {target: {value: 'Where next?'}});
    fireEvent.click(screen.getByText('Ask DeckPilot'));
    await screen.findByText('Looking for your next step…');
    fireEvent.click(screen.getByText('Cancel'));
    await waitFor(() => expect(bridge.status.active).toBe(null));
    bridge.delay = false;
    await act(async () => { await controller.send('How do I proceed?'); });
    await screen.findByText('Look at the symbol on the door. If a detail is missing, describe it.');
    expect(popup.show).toHaveBeenCalledTimes(1);
    await controller.close();
  });
  it('localizes error codes and keeps Settings available', async () => {
    const {bridge, controller} = await setup(true); bridge.failNext = true;
    await act(async () => { await controller.send('Test'); });
    expect(screen.getByRole('alert').textContent).toContain('We could not reach the AI service');
    await act(async () => { await controller.updateSettings({uiLanguage: 'it'}); bridge.failNext = true; await controller.send('Test'); });
    expect(screen.getByRole('alert').textContent).toContain('Non è stato possibile raggiungere');
    expect(screen.getByRole('button', {name: 'Impostazioni'})).toBeTruthy();
    await controller.close();
  });
  it('never sends an image before per-image approval', async () => {
    const {bridge, controller} = await setup(true);
    const file = new File(['synthetic'], 'test.png', {type: 'image/png'});
    Object.defineProperty(file, 'arrayBuffer', {value: async () => new Uint8Array([1, 2, 3]).buffer});
    fireEvent.change(screen.getByLabelText('Game image file'), {target: {files: [file]}});
    await screen.findByAltText('Image to be shared, with metadata removed');
    fireEvent.change(screen.getByLabelText('Or ask a question'), {target: {value: 'What is visible?'}});
    expect((screen.getByText('Help me now') as HTMLButtonElement).disabled).toBe(true);
    fireEvent.click(screen.getByText('Allow this image to be shared'));
    await waitFor(() => expect((screen.getByText('Help me now') as HTMLButtonElement).disabled).toBe(false));
    fireEvent.click(screen.getByText('Help me now'));
    await waitFor(() => expect(bridge.calls.some(c => c.method === 'start_assistant_request' && c.payload.imageRef === 'harness-image')).toBe(true));
    expect(String(bridge.calls.find(c => c.method === 'start_assistant_request')?.payload.text)).toContain('separate observations from guesses');
    await controller.close();
  });
  it('does not offer automatic capture when the capability is absent', async () => {
    const {bridge, controller} = await setup(true);
    expect(screen.getByText('Automatic screen analysis needs verified game capture. Manual images still work.')).toBeTruthy();
    expect(screen.queryByLabelText(/Allow game images to be captured/)).toBe(null);
    expect(bridge.calls.some(c => c.method === 'prepare_capture')).toBe(false);
    await controller.close();
  });
});
