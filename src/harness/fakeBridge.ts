// Offline preview/test harness only. Never imported by src/index.tsx.
import type { AssistantResult, Bridge, GameContext, Settings, Status } from '../domain/types';
import fixture from '../../tests/fixtures/contract.json';
import { SafeError } from '../services/controller';
export function fixtureStatus(): Status {
  return {
    schemaVersion: 1, context: fixture.context as GameContext, history: [], requests: [], active: null,
    tts: {state: 'idle'}, auto: {paused: false, attempts: 0, limit: 20, errors: 0},
    capabilities: {capture: false, images: true, tts: {local: false, openai: true, syntheticVoice: true}},
    diagnostics: {mode: 'HARNESS OFFLINE · nessuna API reale', hardwareValidated: false},
    settings: {
      schemaVersion: 1, provider: null, model: '', remoteConsent: false, endpointConsent: false,
      ollamaEndpoint: 'http://127.0.0.1:11434', visionConfirmed: false, spoiler: 'full_solutions',
      popupDurationMs: 6000, hintIntervalSeconds: 90, voiceEnabled: true, ttsEngine: 'local',
      ttsConsent: false, ttsModel: 'gpt-4o-mini-tts', ttsVoice: 'coral', volume: 0.8,
      persistentHistory: false, imagesEnabled: false, autoHints: false, ollamaTimeoutSeconds: 90,
      configured: {openai: false, gemini: false, claude: false, ollama: false}
    }
  };
}
export class FakeBridge implements Bridge {
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
      if (typeof payload.paused === 'boolean') this.status.auto.paused = payload.paused;
      return {} as T;
    }
    if (method === 'start_assistant_request') {
      if (this.failNext) { this.failNext = false; throw new SafeError('Errore provider sintetico. Riprova.'); }
      if (!this.status.settings.provider) throw new SafeError('Configura prima un provider (harness).');
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
    if (method === 'prepare_image') return {imageRef: 'harness-image', preview: `data:${payload.mime};base64,${payload.dataBase64}`, width: 128, height: 80,
      destination: {provider: this.status.settings.provider, model: this.status.settings.model, endpoint: 'HARNESS'}} as T;
    if (method === 'approve_image_send' || method === 'discard_image') return {} as T;
    if (method === 'start_tts') { this.status.tts = {state: 'error', requestId: String(payload.requestId), sessionId: this.status.context?.sessionId,
      contextRevision: this.status.context?.revision, error: {code: 'VOICE_UNAVAILABLE', message: 'Voce non disponibile (harness)', retryable: false}}; return this.status.tts as T; }
    if (method === 'stop_tts') { this.status.tts = {state: 'idle'}; return this.status.tts as T; }
    if (method === 'clear_history') { this.status.history = []; this.status.requests = []; return {} as T; }
    if (method === 'delete_local_data') { this.status = fixtureStatus(); this.status.context = null; return {} as T; }
    if (method === 'test_provider') return {mode: 'offline'} as T;
    throw new SafeError('RPC non implementata nel solo harness');
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
