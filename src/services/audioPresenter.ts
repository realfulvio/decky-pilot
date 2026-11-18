import type { AudioPort } from '../domain/types';
export class AudioPresenter implements AudioPort {
  private audio?: HTMLAudioElement;
  private url?: string;
  async play(base64: string, mime: string, volume: number, onEnded: () => void) {
    this.stop();
    if (mime !== 'audio/wav' || base64.length > 10_666_672) throw new Error('Invalid audio');
    const bytes = Uint8Array.from(atob(base64), c => c.charCodeAt(0));
    const url = URL.createObjectURL(new Blob([bytes], {type: mime}));
    this.url = url;
    const audio = new Audio(url);
    this.audio = audio;
    audio.volume = Math.max(0, Math.min(1, volume));
    audio.onended = () => { this.stop(); onEnded(); };
    audio.onerror = () => { this.stop(); onEnded(); };
    try { await audio.play(); }
    catch (error) { this.stop(); throw error; }
  }
  stop() {
    if (this.audio) {
      this.audio.onended = null; this.audio.onerror = null;
      this.audio.pause(); this.audio.removeAttribute('src'); this.audio.load(); this.audio = undefined;
    }
    if (this.url) { URL.revokeObjectURL(this.url); this.url = undefined; }
  }
}
