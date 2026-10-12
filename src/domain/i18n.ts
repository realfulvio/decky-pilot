import en from '../../locales/en.json';
import it from '../../locales/it.json';
export type Language = 'en' | 'it';
export type MessageKey = keyof typeof en;
const catalogs: Record<Language, Record<MessageKey, string>> = { en, it };
export function translate(language: Language = 'en', key: MessageKey, values: Record<string, string | number> = {}) {
  return catalogs[language][key].replace(/\{(\w+)\}/g, (match, name: string) => String(values[name] ?? match));
}
export function errorKey(code?: string): MessageKey {
  const key = `error.${code}` as MessageKey;
  return key in en ? key : 'error.INTERNAL_ERROR';
}
