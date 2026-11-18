import type { AssistantResult, GameContext } from './types';
export function isObject(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}
export function isResult(value: unknown): value is AssistantResult {
  return isObject(value) && value.schemaVersion === 1 &&
    ['requestId', 'sessionId', 'model', 'answer', 'popupText', 'speechText'].every(
      k => typeof value[k] === 'string') && typeof value.contextRevision === 'number' &&
    Number.isInteger(value.contextRevision) && typeof value.provider === 'string' &&
    ['chatgpt', 'openai', 'gemini', 'claude', 'grok', 'ollama'].includes(value.provider) &&
    (value.answer as string).length <= 16000 && (value.popupText as string).length <= 240 &&
    (value.speechText as string).length <= 1000 && isObject(value.usage);
}
export function isCurrent(value: {sessionId?: string; contextRevision?: number}, context: GameContext | null) {
  return !!context && value.sessionId === context.sessionId && value.contextRevision === context.revision;
}
export function validateContext(title: string, objective: string, location: string, notes: string) {
  return !!title.trim() && title.length <= 200 && [objective, location, notes].every(v => v.length <= 4000) &&
    objective.length + location.length + notes.length <= 8000;
}
