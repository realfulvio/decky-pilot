import { definePlugin, FileSelectionType, openFilePicker, toaster } from '@decky/api';
import { Router, staticClasses } from '@decky/ui';
import { App } from './components/App';
import { deckyControls } from './components/DeckyControls';
import { Controller } from './services/controller';
import { deckyBridge } from './services/deckyBridge';
import { PopupPresenter } from './services/popupPresenter';
import { AudioPresenter } from './services/audioPresenter';
import { detectGame, GameContextAdapter } from './services/gameContextAdapter';
import { PRODUCT_NAME } from './domain/brand';
import menuIcon from '../assets/brand/decky-pilot-menu.svg';

export default definePlugin(() => {
  const controller = new Controller(deckyBridge, new PopupPresenter(data => toaster.toast(data)), new AudioPresenter());
  const contextAdapter = new GameContextAdapter(controller, Router);
  let dismounted = false;
  void controller.start().then(() => { if (!dismounted) contextAdapter.start(); });
  return {
    name: PRODUCT_NAME, titleView: <div className={staticClasses.Title}>{PRODUCT_NAME}</div>,
    content: <App openExternal={url => {
      if (!url.startsWith('https://auth.openai.com/api/accounts/authorize?')) throw new Error('Unexpected authorization origin');
      SteamClient.System.OpenInSystemBrowser(url);
    }} closeMenus={() => Router.CloseSideMenus()} controller={controller} controls={deckyControls} detectGame={() => detectGame(Router)} pickImage={async () => {
      const root = controller.snapshot().status?.capabilities.importRoot;
      if (!root) return null;
      const selected = await openFilePicker(FileSelectionType.FILE, root, true, false, undefined, ['png', 'jpg', 'jpeg'], false, false, 1);
      const name = selected.realpath.split('/').pop();
      if (!name || selected.realpath !== `${root}/${name}`) throw new Error('Outside import root');
      return name;
    }} />,
    icon: <img src={menuIcon} alt={PRODUCT_NAME} width={24} height={24} />,
    onDismount() { dismounted = true; contextAdapter.stop(); void controller.close(); }
  };
});
