import type { Controller } from './controller';
import { isObject } from '../domain/validation';
export function detectGame(router: unknown) {
  try {
    if (!isObject(router)) return null;
    const running = router.RunningApps;
    if (!Array.isArray(running) || running.length !== 1) return null;
    const app = router.MainRunningApp;
    if (!isObject(app) || typeof app.display_name !== 'string' || !app.display_name.trim()) return null;
    const id = String(app.appid ?? '');
    if (!/^\d{1,20}$/.test(id) || !isObject(running[0]) || String(running[0].appid) !== id) return null;
    return {title: app.display_name.slice(0, 200), appId: id, source: 'steam_internal' as const};
  } catch { return null; }
}
export class GameContextAdapter {
  private timer?: ReturnType<typeof setInterval>;
  private syncing = false;
  private observedId?: string;
  constructor(private controller: Controller, private router: unknown) {}
  available() { return detectGame(this.router) !== null; }
  async sync() {
    if (this.syncing) return;
    const game = detectGame(this.router);
    const current = this.controller.snapshot().status?.context;
    if (!game) {
      if (current?.source === 'steam_internal') {
        this.syncing = true;
        try {
          await this.controller.setContext({title: current.title, appId: current.appId,
            objective: current.objective, location: current.location, userNotes: current.userNotes,
            source: 'unknown'});
        } finally { this.syncing = false; }
      }
      return;
    }
    const changed = this.observedId !== undefined && this.observedId !== game.appId;
    this.observedId = game.appId;
    if (current?.source === 'manual' && !changed) return;
    if (current?.appId === game.appId && current.source === 'steam_internal') {
      await this.controller.bridge.rpc('observe_active_game', {appId:game.appId}).catch(() => undefined);
      return;
    }
    this.syncing = true;
    try { await this.controller.setContext(game); }
    finally { this.syncing = false; }
  }
  start() { if (!this.timer) this.timer = setInterval(() => { void this.sync(); }, 5000); }
  stop() { if (this.timer) clearInterval(this.timer); this.timer = undefined; }
}
