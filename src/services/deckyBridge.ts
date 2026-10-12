import { addEventListener, callable, removeEventListener } from '@decky/api';
import type { Bridge, RpcError } from '../domain/types';
import { SafeError } from './controller';
const rpc = callable<[method: string, payload: Record<string, unknown>], {ok: boolean; data?: unknown; error?: RpcError}>('rpc');
export const deckyBridge: Bridge = {
  async rpc<T>(method: string, payload = {}) {
    const response = await rpc(method, payload);
    if (!response.ok) throw new SafeError(response.error?.code ?? 'INTERNAL_ERROR');
    return response.data as T;
  },
  listen(event, callback) {
    const listener = addEventListener<[unknown]>(event, callback);
    return () => removeEventListener(event, listener);
  }
};
