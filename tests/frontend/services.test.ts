import { describe, expect, it, vi } from 'vitest';
import Ajv from 'ajv';
import schema from '../../contracts/rpc-v1.schema.json';
import fixture from '../fixtures/contract.json';
import { isResult } from '../../src/domain/validation';
import { PopupPresenter } from '../../src/services/popupPresenter';
import { detectGame } from '../../src/services/gameContextAdapter';
import { Controller } from '../../src/services/controller';
import { FakeBridge } from '../../src/harness/fakeBridge';
import { AudioPresenter } from '../../src/services/audioPresenter';
import type { AssistantResult } from '../../src/domain/types';
describe('contracts and presenters', () => {
  it('shared fixtures validate in TypeScript and Python', () => {
    for (const [kind, value] of Object.entries(fixture)) {
      const ajv = new Ajv();
      expect(ajv.compile({...schema, $ref: `#/definitions/${kind}`})(value)).toBe(true);
    }
    expect(isResult(fixture.result)).toBe(true);
    expect(isResult({...fixture.result, popupText: 'x'.repeat(241)})).toBe(false);
    expect(isResult({...fixture.result, provider: 'fake'})).toBe(false);
  });
  it('popup uses 6000ms without sound and dismisses on cleanup', () => {
    const dismiss = vi.fn();
    const toast = vi.fn(() => ({dismiss}));
    const presenter = new PopupPresenter(toast);
    presenter.show(fixture.result as AssistantResult);
    expect(toast).toHaveBeenCalledWith({title: 'Decky Pilot', body: fixture.result.popupText, duration: 6000, playSound: false});
    presenter.clear();
    expect(dismiss).toHaveBeenCalledOnce();
  });
  it('internal Steam shape, undefined and ambiguity', () => {
    const app = {appid: '123', display_name: 'Title'};
    expect(detectGame(undefined)).toBe(null);
    expect(detectGame({MainRunningApp: app, RunningApps: [app, app]})).toBe(null);
    expect(detectGame({MainRunningApp: app, RunningApps: [app]})).toEqual({title: 'Title', appId: '123', source: 'steam_internal'});
    expect(detectGame({get MainRunningApp() { throw new Error(); }, RunningApps: [app]})).toBe(null);
  });
  it('listeners precede requests, stale results are ignored and cleanup removes the timer', async () => {
    const bridge = new FakeBridge();
    bridge.status.settings.voiceEnabled = false;
    const popup = {show: vi.fn(), clear: vi.fn()};
    const controller = new Controller(bridge, popup, {play: vi.fn(), stop: vi.fn()});
    await controller.start();
    expect(bridge.listeners.get('assistant_result')?.size).toBe(1);
    bridge.emit('assistant_result', {...fixture.result, sessionId: 'previous'});
    expect(popup.show).not.toHaveBeenCalled();
    bridge.emit('assistant_result', fixture.result);
    bridge.emit('assistant_result', fixture.result);
    expect(popup.show).toHaveBeenCalledOnce();
    await controller.close();
    expect([...bridge.listeners.values()].every(set => set.size === 0)).toBe(true);
  });
  it('polling recovers chat without paying for TTS again after reload', async () => {
    const bridge = new FakeBridge();
    bridge.status.requests = [{...fixture.request, kind: 'manual', state: 'completed', result: fixture.result as AssistantResult}];
    const controller = new Controller(bridge, {show: vi.fn(), clear: vi.fn()}, {play: vi.fn(), stop: vi.fn()});
    await controller.start();
    expect(bridge.calls.some(c => c.method === 'start_tts')).toBe(false);
    await controller.close();
  });
  it('audio stop releases the object URL when playback fails', async () => {
    const pause = vi.fn(), load = vi.fn(), removeAttribute = vi.fn();
    vi.stubGlobal('Audio', class {pause = pause; load = load; removeAttribute = removeAttribute; play = vi.fn(async () => { throw new Error('unavailable'); });});
    URL.createObjectURL = vi.fn(() => 'blob:test');
    URL.revokeObjectURL = vi.fn();
    const audio = new AudioPresenter();
    await expect(audio.play(btoa('RIFF0000WAVE'), 'audio/wav', 0.8, vi.fn())).rejects.toThrow();
    expect(URL.revokeObjectURL).toHaveBeenCalledWith('blob:test');
    expect(pause).toHaveBeenCalledOnce();
    vi.unstubAllGlobals();
  });
});
