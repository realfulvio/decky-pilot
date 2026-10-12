import { afterEach, describe, expect, it, vi } from 'vitest';
import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { App } from '../../src/components/App';
import { harnessControls } from '../../src/harness/controls';
import { FakeBridge } from '../../src/harness/fakeBridge';
import { Controller } from '../../src/services/controller';
import { translate } from '../../src/domain/i18n';
import type { GameContext } from '../../src/domain/types';
import en from '../../locales/en.json';
import itCatalog from '../../locales/it.json';
afterEach(cleanup);
async function setup(ready = false, detectGame?: () => Partial<GameContext> | null) {
  const bridge = new FakeBridge();
  if (ready) Object.assign(bridge.status.settings, {provider: 'openai', model: 'sample', configured: {openai: true}, remoteConsent: true, imagesEnabled: true, visionConfirmed: true});
  const popup = {show: vi.fn(), clear: vi.fn()}; const audio = {play: vi.fn(), stop: vi.fn()};
  const controller = new Controller(bridge, popup, audio); await controller.start();
  render(<App controller={controller} controls={harnessControls} detectGame={detectGame} />);
  return {bridge, controller, popup, audio};
}
describe('English-first UI and complete Italian localization', () => {
  it('shows only returned catalog names and preserves unknown vision restrictions', async () => {
    const {bridge, controller} = await setup();
    bridge.catalog = [{id:'returned-account-slug',label:'Name returned by the account',images:false,verification:'unconfirmed'}];
    fireEvent.click(screen.getByRole('button', {name:'Settings'}));
    fireEvent.change(screen.getByLabelText('AI service'), {target:{value:'chatgpt'}});
    expect(screen.queryByRole('option', {name:/GPT-6.1/})).toBeNull();
    expect(screen.queryByLabelText('API key')).toBeNull();
    fireEvent.click(screen.getByText('Load available models'));
    await screen.findByRole('option', {name:'Name returned by the account · image input unverified'});
    expect(bridge.calls.find(call => call.method === 'list_models')?.payload).toEqual({provider:'chatgpt',consent:true});
    expect(bridge.calls.some(call => call.method === 'start_assistant_request')).toBe(false);
    await controller.close();
  });
  it('keeps Grok API billing separate from consumer subscriptions', async () => {
    const {bridge, controller} = await setup();
    fireEvent.click(screen.getByRole('button', {name:'Settings'}));
    fireEvent.change(screen.getByLabelText('AI service'), {target:{value:'grok'}});
    expect(screen.getByText(/API keys connect a developer API/)).toBeTruthy();
    expect(screen.getByLabelText('API key')).toBeTruthy();
    expect(screen.queryByText('Continue with ChatGPT')).toBeNull();
    expect(bridge.calls.some(call => call.method === 'start_assistant_request')).toBe(false);
    await controller.close();
  });
  it('includes the player question in Help me now without an automatic provider change', async () => {
    const {bridge, controller} = await setup(true);
    bridge.status.settings.imagesEnabled = false;
    await act(async () => {await controller.refresh();});
    fireEvent.change(screen.getByLabelText('Ask a question'), {target:{value:'I tried the lever. What next?'}});
    fireEvent.click(screen.getByText('Help me now'));
    await waitFor(() => expect(bridge.calls.find(call => call.method === 'start_assistant_request')?.payload.text).toContain('I tried the lever. What next?'));
    expect(bridge.status.settings.provider).toBe('openai');
    await controller.close();
  });
  it.each(['revision', 'session', 'cleared'] as const)('refreshes all game fields after a %s context event', async change => {
    const {bridge, controller} = await setup(true);
    fireEvent.click(screen.getByRole('button', {name: 'Game'}));
    fireEvent.click(screen.getByText('Advanced options'));
    for (const label of ['Game title', 'What are you trying to do?', 'Where are you? (optional)', 'Anything else we should know?', 'Steam AppID (optional)']) {
      fireEvent.change(screen.getByLabelText(label), {target: {value: label.includes('AppID') ? '123' : 'Old draft'}});
    }
    await act(async () => {
      bridge.status.context = change === 'cleared' ? null : {...bridge.status.context!,
        title: 'New game', appId: '456', objective: 'New objective', location: 'New area', userNotes: 'New notes',
        ...(change === 'session' ? {sessionId: 'new-session'} : {revision: bridge.status.context!.revision + 1})};
      bridge.emit('context_changed', bridge.status.context);
      await controller.refresh();
    });
    const expected = change === 'cleared' ? ['', '', '', '', ''] : ['New game', 'New objective', 'New area', 'New notes', '456'];
    ['Game title', 'What are you trying to do?', 'Where are you? (optional)', 'Anything else we should know?', 'Steam AppID (optional)'].forEach((label, index) => {
      expect((screen.getByLabelText(label) as HTMLInputElement).value).toBe(expected[index]);
    });
    if (change !== 'cleared') {
      fireEvent.click(screen.getByText('Save game'));
      await waitFor(() => expect(bridge.calls.find(call => call.method === 'set_game_context')?.payload).toMatchObject({title: 'New game', appId: '456', objective: 'New objective', location: 'New area', userNotes: 'New notes'}));
    }
    await controller.close();
  });
  it('preserves an unsaved game draft during status polling and unrelated settings updates', async () => {
    const {controller} = await setup(true);
    fireEvent.click(screen.getByRole('button', {name: 'Game'}));
    fireEvent.change(screen.getByLabelText('Game title'), {target: {value: 'Unsaved title'}});
    await act(async () => { await controller.refresh(); await controller.updateSettings({voiceEnabled: false}); });
    expect((screen.getByLabelText('Game title') as HTMLInputElement).value).toBe('Unsaved title');
    await controller.close();
  });
  it.each([false, true])('updates the draft when choosing the detected Steam game (onboarding=%s)', async onboarding => {
    const detected = {title: 'Detected game', appId: '789', objective: '', location: '', userNotes: '', source: 'steam_internal' as const};
    const {bridge, controller} = await setup(!onboarding, () => detected);
    fireEvent.click(screen.getByText(onboarding ? 'Get started' : 'Game'));
    fireEvent.change(screen.getByLabelText('Game title'), {target: {value: 'Stale game'}});
    fireEvent.click(screen.getByText('Use detected game'));
    await waitFor(() => expect((screen.getByLabelText('Game title') as HTMLInputElement).value).toBe('Detected game'));
    fireEvent.click(screen.getByText('Save game'));
    await waitFor(() => expect(bridge.calls.filter(call => call.method === 'set_game_context')).toHaveLength(2));
    expect(bridge.calls.filter(call => call.method === 'set_game_context')[1].payload).toMatchObject({title: 'Detected game', appId: '789', objective: '', location: '', userNotes: ''});
    await controller.close();
  });
  it('keeps chat and online voice credentials separate and never sends setup requests', async () => {
    const {bridge,controller}=await setup(true);
    fireEvent.click(screen.getByRole('button',{name:'Settings'}));
    fireEvent.change(screen.getByLabelText('API key'),{target:{value:'synthetic-chat-key'}});
    fireEvent.change(screen.getByLabelText('Voice service'),{target:{value:'openai'}});
    const speech=screen.getByLabelText('OpenAI voice API key') as HTMLInputElement;
    fireEvent.change(speech,{target:{value:'synthetic-speech-key'}});
    fireEvent.click(screen.getByText('Save OpenAI voice key'));
    await waitFor(()=>expect(speech.value).toBe(''));
    expect((screen.getByLabelText('API key') as HTMLInputElement).value).toBe('synthetic-chat-key');
    expect(bridge.calls.find(call=>call.method==='set_api_key')?.payload.provider).toBe('openai');
    expect(bridge.calls.some(call=>['start_assistant_request','test_provider','start_tts'].includes(call.method))).toBe(false);
    expect(bridge.status.settings.provider).toBe('openai');
    await controller.close();
  });
  it('has identical catalog keys and interpolation fields', () => {
    expect(Object.keys(itCatalog).sort()).toEqual(Object.keys(en).sort());
    for (const key of Object.keys(en) as (keyof typeof en)[]) {
      expect(itCatalog[key].match(/\{\w+\}/g)?.sort()).toEqual(en[key].match(/\{\w+\}/g)?.sort());
      expect(itCatalog[key].trim()).not.toBe('');
    }
    expect(translate('it', 'helpNow')).toBe('Aiutami ora');
    expect(translate('unknown' as 'en', 'helpNow')).toBe('Help me now');
    expect(translate('en','imageDestination',{provider:'OpenAI',model:'gpt-4.1'})).toContain('OpenAI');
  });
  it('onboarding is English, sends no AI requests and clears the saved key', async () => {
    const {bridge, controller} = await setup();
    expect(screen.getByText('Let’s get you unstuck')).toBeTruthy();
    expect(screen.getByAltText('Decky Pilot').getAttribute('src')).toContain('decky-pilot-logo-dark.png');
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
    fireEvent.change(screen.getByLabelText('Lingua dell’assistente (risposte e voce)'), {target: {value: 'it'}});
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
    fireEvent.change(screen.getByLabelText('Ask a question'), {target: {value: 'Where next?'}});
    fireEvent.click(screen.getByText('Ask Decky Pilot'));
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
    fireEvent.change(screen.getByLabelText('Ask a question'), {target: {value: 'What is visible?'}});
    expect((screen.getByText('Help me now') as HTMLButtonElement).disabled).toBe(true);
    fireEvent.click(screen.getByText('Allow this image to be shared'));
    await waitFor(() => expect((screen.getByText('Help me now') as HTMLButtonElement).disabled).toBe(false));
    fireEvent.click(screen.getByText('Help me now'));
    await waitFor(() => expect(bridge.calls.some(c => c.method === 'start_assistant_request' && c.payload.imageRef === 'harness-image')).toBe(true));
    expect(String(bridge.calls.find(c => c.method === 'start_assistant_request')?.payload.text)).toContain('observations from deductions');
    await controller.close();
  });
  it('does not offer automatic capture when the capability is absent', async () => {
    const {bridge, controller} = await setup(true);
    fireEvent.click(screen.getByText('Automatic help'));
    expect(screen.getByText('Automatic screen analysis needs verified game capture. Manual images still work.')).toBeTruthy();
    expect(screen.queryByLabelText(/Allow game images to be captured/)).toBe(null);
    expect(bridge.calls.some(c => c.method === 'prepare_capture')).toBe(false);
    await controller.close();
  });
});
