export type ProviderId = 'openai' | 'gemini' | 'claude' | 'ollama';
export type SpoilerLevel = 'none' | 'hints' | 'full_solutions';
export interface Settings {
  uiLanguage: 'en' | 'it'; responseLanguage: 'en' | 'it'; ttsLanguage: 'en' | 'it'; captureEnabled: boolean;
  schemaVersion: 1; provider: ProviderId | null; model: string; remoteConsent: boolean;
  ollamaEndpoint: string; endpointConsent: boolean; visionConfirmed: boolean; spoiler: SpoilerLevel;
  popupDurationMs: number; hintIntervalSeconds: number; voiceEnabled: boolean; ttsEngine: 'local' | 'openai';
  ttsConsent: boolean; ttsModel: string; ttsVoice: string; volume: number; persistentHistory: boolean;
  imagesEnabled: boolean; autoHints: boolean; ollamaTimeoutSeconds: number;
  configured: Record<ProviderId, boolean>;
}
export interface GameContext {
  gameKey: string; appId: string; title: string; source: 'manual' | 'steam_internal' | 'unknown';
  sessionId: string; revision: number; observedAt: string; objective: string; location: string; userNotes: string;
}
export interface AssistantRequest {
  requestId: string; sessionId: string; contextRevision: number; kind: 'manual' | 'auto_hint';
  text: string; imageRef?: string;
}
export interface AssistantResult {
  schemaVersion: 1; requestId: string; sessionId: string; contextRevision: number; provider: ProviderId;
  model: string; answer: string; popupText: string; speechText: string;
  usage: {inputTokens?: number; outputTokens?: number};
}
export interface RpcError { code: string; message: string; retryable: boolean; retryAfterMs?: number }
export interface RequestState {
  requestId: string; sessionId: string; contextRevision: number; kind: 'manual' | 'auto_hint';
  state: 'pending' | 'completed' | 'error' | 'cancelled' | 'duplicate'; result?: AssistantResult; error?: RpcError;
}
export interface VoiceState {
  state: 'idle' | 'pending' | 'ready' | 'error'; requestId?: string; sessionId?: string;
  contextRevision?: number; mime?: string; audioBase64?: string; error?: RpcError;
}
export interface Status {
  schemaVersion: 1; settings: Settings; context: GameContext | null;
  history: {role: 'user' | 'assistant'; content: string; at: number}[];
  requests: RequestState[]; active: string | null; tts: VoiceState;
  pendingImageRef?: string | null;
  auto: {paused: boolean; attempts: number; limit: number; errors: number; sessionConsent?: boolean; visual?: boolean};
  capabilities: {capture: boolean; images: boolean; importRoot?: string; tts: {local: boolean; openai: boolean; syntheticVoice: boolean}};
  diagnostics: Record<string, string | boolean | number>;
}
export interface PreparedImage {
  imageRef: string; preview: string; width: number; height: number;
  destination: {provider: ProviderId; model: string; endpoint: string};
}
export interface Bridge {
  rpc<T>(method: string, payload?: Record<string, unknown>): Promise<T>;
  listen(event: string, callback: (payload: unknown) => void): () => void;
}
export interface PopupPort { show(result: AssistantResult, duration: number): void; clear(): void }
export interface AudioPort {
  play(base64: string, mime: string, volume: number, onEnded: () => void): Promise<void>;
  stop(): void;
}
