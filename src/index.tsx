import { definePlugin, FileSelectionType, openFilePicker, toaster } from '@decky/api';
import { Router, staticClasses } from '@decky/ui';
import { App } from './components/App';
import { deckyControls } from './components/DeckyControls';
import { Controller } from './services/controller';
import { deckyBridge } from './services/deckyBridge';
import { PopupPresenter } from './services/popupPresenter';
import { AudioPresenter } from './services/audioPresenter';
import { detectGame, GameContextAdapter } from './services/gameContextAdapter';

export default definePlugin(() => {
  const controller = new Controller(deckyBridge, new PopupPresenter(data => toaster.toast(data)), new AudioPresenter());
  const contextAdapter = new GameContextAdapter(controller, Router);
  let dismounted = false;
  void controller.start().then(() => { if (!dismounted) contextAdapter.start(); });
  return {
    name: 'DeckPilot', titleView: <div className={staticClasses.Title}>DeckPilot</div>,
    content: <App controller={controller} controls={deckyControls} detectGame={() => detectGame(Router)} pickImage={async () => {
      const root = controller.snapshot().status?.capabilities.importRoot;
      if (!root) return null;
      const selected = await openFilePicker(FileSelectionType.FILE, root, true, false, undefined, ['png', 'jpg', 'jpeg'], false, false, 1);
      const name = selected.realpath.split('/').pop();
      if (!name || selected.realpath !== `${root}/${name}`) throw new Error('Outside import root');
      return name;
    }} />,
    icon: <span aria-label="DeckPilot">DP</span>,
    onDismount() { dismounted = true; contextAdapter.stop(); void controller.close(); }
  };
});
