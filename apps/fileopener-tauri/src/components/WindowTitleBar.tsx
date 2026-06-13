import { type MouseEvent } from 'react';
import { getCurrentWindow } from '@tauri-apps/api/window';
import appIcon from '../assets/app-icon.png';

export function WindowTitleBar() {
  const appWindow = getCurrentWindow();

  const startDrag = (event: MouseEvent<HTMLDivElement>) => {
    if (event.button !== 0) {
      return;
    }

    void appWindow.startDragging();
  };

  return (
    <div className="window-titlebar" onMouseDown={startDrag}>
      <div className="window-titlebar-title">
        <img className="window-titlebar-icon" src={appIcon} alt="" aria-hidden="true" />
        <span>文件批量打开工具</span>
      </div>
      <div className="window-titlebar-controls" onMouseDown={(event) => event.stopPropagation()}>
        <button
          className="window-control"
          type="button"
          aria-label="最小化"
          title="最小化"
          onClick={() => void appWindow.minimize()}
        >
          <span aria-hidden="true">─</span>
        </button>
        <button
          className="window-control"
          type="button"
          aria-label="最大化或还原"
          title="最大化或还原"
          onClick={() => void appWindow.toggleMaximize()}
        >
          <span className="window-restore-icon" aria-hidden="true">
            <span className="window-restore-icon-back" />
            <span className="window-restore-icon-front" />
          </span>
        </button>
        <button
          className="window-control window-control-close"
          type="button"
          aria-label="关闭"
          title="关闭"
          onClick={() => void appWindow.close()}
        >
          <span aria-hidden="true">×</span>
        </button>
      </div>
    </div>
  );
}
