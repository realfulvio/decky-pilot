import type { AudioPort, AssistantResult, Bridge, GameContext, PopupPort, PreparedImage, Settings, Status, VoiceState } from '../domain/types';
import { type MessageKey, errorKey, translate } from '../domain/i18n';
import { isCurrent, isObject, isResult } from '../domain/validation';

export interface ViewState { status: Status | null; error: MessageKey | ''; voice: MessageKey }
export class Controller {
  private state: ViewState = {status: null, error: '', voice: 'voiceIdle'};
  private subscribers = new Set<() => void>();
  private cleanups: (() => void)[] = [];
  private shown = new Set<string>();
  private played = new Set<string>();
  private timer?: ReturnType<typeof setInterval>;
  private closed = false;
  private refreshTask?: Promise<void>;
  constructor(public readonly bridge: Bridge, private popup: PopupPort, private audio: AudioPort) {}
  snapshot = () => this.state;
  subscribe = (callback: () => void) => { this.subscribers.add(callback); return () => this.subscribers.delete(callback); };
  private update(patch: Partial<ViewState>) {
    if (this.closed) return;
    this.state = {...this.state, ...patch};
    this.subscribers.forEach(callback => callback());
  }
  async start() {
    if (this.closed || this.cleanups.length) return;
    // Plugin-wide listeners exist before starting any request and outlive panel mounts.
    this.cleanups = ['assistant_result', 'assistant_error', 'request_state', 'context_changed', 'tts_state'].map(event =>
      this.bridge.listen(event, payload => {
        if (this.closed) return;
        if (event === 'context_changed') { this.audio.stop(); this.popup.clear(); }
        if (event === 'assistant_result' && isResult(payload)) this.present(payload);
        if (event === 'assistant_error' && isObject(payload) && isCurrent(payload, this.state.status?.context ?? null)) {
          const error = payload.error;
          if (isObject(error) && typeof error.code === 'string') this.update({error: errorKey(error.code)});
        }
        if (event === 'tts_state' && isObject(payload)) void this.presentVoice(payload as unknown as VoiceState);
        void this.refresh();
      }));
    await this.refresh();
    if (this.closed) return;
    this.timer = setInterval(() => { void this.refresh(); }, 5000);
  }
  async refresh() {
    if (this.closed) return;
    while (this.refreshTask) await this.refreshTask;
    if (this.closed) return;
    const task = this.readStatus();
    this.refreshTask = task;
    try { await task; } finally { if (this.refreshTask === task) this.refreshTask = undefined; }
  }
  private async readStatus() {
    try {
      const status = await this.bridge.rpc<Status>('get_status');
      if (this.closed) return;
      const previous = this.state.status?.context;
      if (previous && (!status.context || previous.sessionId !== status.context.sessionId || previous.revision !== status.context.revision)) {
        this.audio.stop(); this.popup.clear();
      }
      this.update({status});
      if (!previous) for (const record of status.requests) {
        if (record.state === 'completed') this.shown.add(record.requestId);
      }
      for (const record of status.requests) {
        if (record.state === 'completed' && isResult(record.result)) this.present(record.result);
        if (record.error && isCurrent(record, status.context)) this.update({error: errorKey(record.error.code)});
      }
      void this.presentVoice(status.tts);
    } catch { this.update({error: 'backendError'}); }
  }
  private present(result: AssistantResult) {
    const status = this.state.status;
    if (!status || !isCurrent(result, status.context) || this.shown.has(result.requestId)) return;
    this.shown.add(result.requestId);
    while (this.shown.size > 100) this.shown.delete(this.shown.values().next().value!);
    try { this.popup.show(result, status.settings.popupDurationMs); }
    catch { this.update({error: 'popupError'}); }
    if (status.settings.voiceEnabled) {
      void this.act('start_tts', {requestId: result.requestId, sessionId: result.sessionId});
    }
  }
  private async presentVoice(voice: VoiceState) {
    if (voice.state === 'idle') {
      this.audio.stop();
      const status = this.state.status;
      this.update({voice: status?.settings.ttsEngine === 'local' && !status.capabilities.tts.local ? 'voiceMissing' : 'voiceIdle'});
      return;
    }
    if (!isCurrent(voice, this.state.status?.context ?? null)) return;
    if (voice.state === 'error') { this.update({voice: 'voiceMissing'}); return; }
    if (voice.state === 'pending') { this.update({voice: 'voicePending'}); return; }
    if (voice.state === 'ready' && voice.audioBase64 && voice.mime && voice.requestId && !this.played.has(voice.requestId)) {
      this.played.add(voice.requestId);
      while (this.played.size > 100) this.played.delete(this.played.values().next().value!);
      try {
        await this.audio.play(voice.audioBase64, voice.mime, this.state.status!.settings.volume,
          () => { void this.act('stop_tts'); });
        this.update({voice: 'voicePlaying'});
      } catch {
        this.update({voice: 'voiceMissing'});
        await this.act('stop_tts');
      }
    }
  }
  async act<T>(method: string, payload: Record<string, unknown> = {}): Promise<T | undefined> {
    try {
      const result = await this.bridge.rpc<T>(method, payload);
      this.update({error: ''});
      await this.refresh();
      return result;
    } catch (error) {
      // Only bridge-sanitized errors are exposed, never arbitrary RPC exceptions.
      this.update({error: error instanceof SafeError ? errorKey(error.code) : 'operationError'});
      return undefined;
    }
  }
  async send(text: string, image?: PreparedImage) {
    const context = this.state.status?.context;
    if (!context) { this.update({error: 'gameRequired'}); return false; }
    const result = await this.act('start_assistant_request', {
      requestId: crypto.randomUUID().replace(/-/g, ''), sessionId: context.sessionId,
      contextRevision: context.revision, kind: 'manual', text, ...(image ? {imageRef: image.imageRef} : {})
    });
    return result !== undefined;
  }
  async helpNow(image?: PreparedImage) {
    const language = this.state.status?.settings.responseLanguage ?? 'en';
    return this.send(translate(language, image ? 'visualPrompt' : 'hintPrompt'), image);
  }
  async updateSettings(settings: Partial<Settings>) { return this.act<Settings>('update_settings', settings); }
  async setContext(context: Partial<GameContext> & {newSession?: boolean}) { return this.act<GameContext>('set_game_context', context); }
  async stopVoice() { this.audio.stop(); this.played.clear(); await this.act('stop_tts'); }
  async readLast() {
    const status = this.state.status;
    const latest = status?.requests.filter(r => r.state === 'completed' && isCurrent(r, status.context)).pop();
    if (!latest) return;
    this.played.delete(latest.requestId);
    await this.act('start_tts', {requestId: latest.requestId, sessionId: latest.sessionId});
  }
  async close() {
    this.closed = true;
    if (this.timer) clearInterval(this.timer);
    this.cleanups.forEach(remove => remove());
    this.cleanups = [];
    this.popup.clear(); this.audio.stop();
    await this.bridge.rpc('stop_tts').catch(() => undefined);
    this.subscribers.clear();
  }
}
export class SafeError extends Error { constructor(public readonly code = 'INTERNAL_ERROR') { super(code); } }
