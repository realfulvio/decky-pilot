// Offline preview/test harness only. Never imported by src/index.tsx.
import type { AssistantResult, Bridge, GameContext, Settings, Status } from '../domain/types';
import fixture from '../../tests/fixtures/contract.json';
import { SafeError } from '../services/controller';
const SYNTHETIC_PNG = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aF9sAAAAASUVORK5CYII=';
export function fixtureStatus(): Status {
  return {
    schemaVersion: 1, context: fixture.context as GameContext, history: [], requests: [], active: null,
    tts: {state: 'idle'}, auto: {paused: false, attempts: 0, limit: 20, errors: 0},
    capabilities: {capture: false, images: true, tts: {local: false, openai: true, syntheticVoice: true}},
    diagnostics: {mode: 'OFFLINE PREVIEW · no real API calls', hardwareValidated: false},
    settings: {
      uiLanguage: 'en', responseLanguage: 'en', ttsLanguage: 'en', captureEnabled: false,
      schemaVersion: 1, provider: null, model: '', remoteConsent: false, endpointConsent: false,
      ollamaEndpoint: 'http://127.0.0.1:11434', visionConfirmed: false, spoiler: 'full_solutions',
      popupDurationMs: 6000, hintIntervalSeconds: 90, voiceEnabled: true, ttsEngine: 'local',
      ttsConsent: false, ttsModel: 'gpt-4o-mini-tts', ttsVoice: 'coral', volume: 0.8,
      persistentHistory: false, imagesEnabled: false, autoHints: false, ollamaTimeoutSeconds: 90,
      configured: {chatgpt: false, openai: false, gemini: false, claude: false, grok: false, ollama: false}
    }
  };
}
export class FakeBridge implements Bridge {
  catalog = [{id:'gpt-4.1',label:'GPT-4.1 (simulated catalog)',images:true,verification:'synthetic_fixture'}];
  status = fixtureStatus();
  calls: {method: string; payload: Record<string, unknown>}[] = [];
  listeners = new Map<string, Set<(value: unknown) => void>>();
  delay = false;
  failNext = false;
  listen(event: string, callback: (value: unknown) => void) {
    const callbacks = this.listeners.get(event) ?? new Set();
    callbacks.add(callback); this.listeners.set(event, callbacks);
    return () => callbacks.delete(callback);
  }
  emit(event: string, payload: unknown) { this.listeners.get(event)?.forEach(callback => callback(payload)); }
  async rpc<T>(method: string, payload: Record<string, unknown> = {}): Promise<T> {
    // Never store key values, even in preview instrumentation.
    this.calls.push({method, payload: {...payload, ...(method === 'set_api_key' ? {key: '[redacted]'} : {})}});
    if (method === 'set_capture_guard') return {blocked: payload.blocked} as T;
    if (method === 'observe_active_game') return {observed:true} as T;
    if (method === 'list_models') return {models: this.catalog,partial:false} as T;
    if (method === 'begin_chatgpt_sign_in') return {authorizationUrl:'https://auth.openai.com/api/accounts/authorize?preview=synthetic'} as T;
    if (method === 'disconnect_chatgpt' || method === 'cancel_chatgpt_sign_in') return {revocationConfirmed:false} as T;
    if (method === 'prepare_capture') throw new SafeError('CAPTURE_UNAVAILABLE');
    if (method === 'get_status') return structuredClone(this.status) as T;
    if (method === 'update_settings') {
      this.status.settings = {...this.status.settings, ...payload} as Settings;
      return structuredClone(this.status.settings) as T;
    }
    if (method === 'set_api_key' || method === 'delete_api_key') {
      this.status.settings.configured[payload.provider as keyof Settings['configured']] = method === 'set_api_key';
      return {configured: method === 'set_api_key'} as T;
    }
    if (method === 'set_game_context') {
      this.status.context = {...fixture.context, ...payload, revision: (this.status.context?.revision ?? 0) + 1} as GameContext;
      this.emit('context_changed', this.status.context);
      return this.status.context as T;
    }
    if (method === 'set_auto_hints') {
      if (typeof payload.enabled === 'boolean') this.status.settings.autoHints = payload.enabled;
      if (typeof payload.consent === 'boolean') this.status.auto.sessionConsent = payload.consent;
      if (typeof payload.visual === 'boolean') this.status.auto.visual = payload.visual;
      if (typeof payload.paused === 'boolean') this.status.auto.paused = payload.paused;
      return {} as T;
    }
    if (method === 'start_assistant_request') {
      if (this.failNext) { this.failNext = false; throw new SafeError('NETWORK_ERROR'); }
      if (!this.status.settings.provider) throw new SafeError('NOT_CONFIGURED');
      const requestId = String(payload.requestId);
      this.status.active = requestId;
      this.status.requests.push({requestId, sessionId: String(payload.sessionId), contextRevision: Number(payload.contextRevision), kind: 'manual', state: 'pending'});
      if (!this.delay) this.complete(payload);
      return {requestId, state: 'pending'} as T;
    }
    if (method === 'cancel_request') {
      const record = this.status.requests.find(r => r.requestId === payload.requestId);
      if (record) record.state = 'cancelled';
      this.status.active = null;
      return {} as T;
    }
    if (method === 'prepare_image' || method === 'prepare_import_image' || method === 'approve_image_send') {
      // Mirrors the backend gates: current session, image consent, destination from saved settings.
      if (!this.status.context || payload.sessionId !== this.status.context.sessionId) throw new SafeError('CONTEXT_STALE');
      if (!this.status.settings.imagesEnabled) throw new SafeError('CONSENT_REQUIRED');
      const {provider, model, ollamaEndpoint} = this.status.settings;
      const destination = {provider, model, endpoint: provider === 'ollama' ? ollamaEndpoint : 'cloud'};
      if (method === 'approve_image_send') {
        if (JSON.stringify(payload.destination) !== JSON.stringify(destination)) throw new SafeError('CONSENT_REQUIRED');
        return {approved: true} as T;
      }
      // Imports are read from the device import folder; the harness substitutes a synthetic 1x1 PNG.
      const preview = method === 'prepare_image' ? `data:${payload.mime};base64,${payload.dataBase64}` : `data:image/png;base64,${SYNTHETIC_PNG}`;
      return {imageRef: 'harness-image', preview, width: 128, height: 80, destination} as T;
    }
    if (method === 'discard_image') return {discarded: true} as T;
    if (method === 'start_tts') { this.status.tts = {state: 'error', requestId: String(payload.requestId), sessionId: this.status.context?.sessionId,
      contextRevision: this.status.context?.revision, error: {code: 'VOICE_UNAVAILABLE', message: 'Voice unavailable (offline preview)', retryable: false}}; return this.status.tts as T; }
    if (method === 'stop_tts') { this.status.tts = {state: 'idle'}; return this.status.tts as T; }
    if (method === 'clear_history') { this.status.history = []; this.status.requests = []; return {} as T; }
    if (method === 'delete_local_data') { this.status = fixtureStatus(); this.status.context = null; return {} as T; }
    if (method === 'test_provider') return {mode: 'offline'} as T;
    throw new SafeError('INVALID_INPUT');
  }
  complete(payload: Record<string, unknown>) {
    const result = {...fixture.result, requestId: payload.requestId, sessionId: payload.sessionId, contextRevision: payload.contextRevision} as AssistantResult;
    this.status.history.push({role: 'user', content: String(payload.text), at: 0}, {role: 'assistant', content: result.answer, at: 0});
    const record = this.status.requests.find(r => r.requestId === payload.requestId);
    if (record) { record.state = 'completed'; record.result = result; }
    this.status.active = null;
    this.emit('assistant_result', result);
  }
}
