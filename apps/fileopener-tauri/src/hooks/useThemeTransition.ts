import { type MouseEvent, useEffect, useState } from 'react';
import { setTheme as setAppTheme } from '@tauri-apps/api/app';
import { getCurrentWindow } from '@tauri-apps/api/window';
import { getInitialThemeMode, toNativeWindowTheme } from '../theme-utils';
import type { ThemeMode } from '../types';

type ViewTransitionDocument = Document & {
  startViewTransition?: (callback: () => void) => {
    ready: Promise<void>;
    finished: Promise<void>;
  };
};

function getInitialTheme(): ThemeMode {
  return getInitialThemeMode(window.localStorage.getItem('fileopener-theme'));
}

function getThemeRevealRadius(x: number, y: number) {
  return Math.hypot(Math.max(x, window.innerWidth - x), Math.max(y, window.innerHeight - y));
}

export function useThemeTransition() {
  const [themeMode, setThemeMode] = useState<ThemeMode>(getInitialTheme);
  const [themeAnimating, setThemeAnimating] = useState(false);

  useEffect(() => {
    const nativeTheme = toNativeWindowTheme(themeMode);

    try {
      void Promise.all([
        setAppTheme(nativeTheme).catch(() => undefined),
        getCurrentWindow().setTheme(nativeTheme).catch(() => undefined)
      ]);
    } catch {
      // Browser preview does not expose the Tauri window API.
    }
  }, [themeMode]);

  const toggleThemeMode = (event?: MouseEvent<HTMLButtonElement>) => {
    if (themeAnimating) {
      return;
    }

    const next = themeMode === 'dark' ? 'light' : 'dark';
    const rect = event?.currentTarget.getBoundingClientRect();
    const originX = rect ? rect.left + rect.width / 2 : window.innerWidth / 2;
    const originY = rect ? rect.top + rect.height / 2 : window.innerHeight / 2;

    const applyTheme = () => {
      setThemeMode(next);
      window.localStorage.setItem('fileopener-theme', next);
    };

    const viewTransitionDocument = document as ViewTransitionDocument;
    if (!viewTransitionDocument.startViewTransition) {
      applyTheme();
      return;
    }

    setThemeAnimating(true);
    const transition = viewTransitionDocument.startViewTransition(applyTheme);

    transition.ready
      .then(() => {
        const radius = getThemeRevealRadius(originX, originY);
        document.documentElement.animate(
          {
            clipPath: [
              `circle(0px at ${originX}px ${originY}px)`,
              `circle(${radius}px at ${originX}px ${originY}px)`
            ]
          },
          {
            duration: 620,
            easing: 'cubic-bezier(0.22, 1, 0.36, 1)',
            pseudoElement: '::view-transition-new(root)'
          }
        );
      })
      .catch(() => undefined);

    transition.finished.finally(() => {
      setThemeAnimating(false);
    });
  };

  return {
    themeMode,
    themeAnimating,
    toggleThemeMode
  };
}
