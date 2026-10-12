import type { AssistantResult, PopupPort } from '../domain/types';
interface Notification {dismiss(): void}
export class PopupPresenter implements PopupPort {
  private handle?: Notification;
  constructor(private toast: (data: {title: string; body: string; duration: number; playSound: boolean}) => Notification) {}
  show(result: AssistantResult, duration = 6000) {
    this.clear();
    this.handle = this.toast({title: 'DeckPilot', body: result.popupText.slice(0, 240), duration, playSound: false});
  }
  clear() { this.handle?.dismiss(); this.handle = undefined; }
}
