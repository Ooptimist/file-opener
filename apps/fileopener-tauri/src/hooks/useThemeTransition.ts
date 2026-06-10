import { type MouseEvent, useState } from 'react';
import type { ThemeMode } from '../types';

type ViewTransitionDocument = Document & {
  startViewTransition?: (callback: () => void) => {
    ready: Promise<void>;
    finished: Promise<void>;
  };
};

function getInitialTheme(): ThemeMode {
  const savedTheme = window.localStorage.getItem('fileopener-theme');
  return savedTheme === 'light' ? 'light' : 'dark';
}

function getThemeRevealRadius(x: number, y: number) {
  return Math.hypot(Math.max(x, window.innerWidth - x), Math.max(y, window.innerHeight - y));
}

export function useThemeTransition() {
  const [themeMode, setThemeMode] = useState<ThemeMode>(getInitialTheme);
  const [themeAnimating, setThemeAnimating] = useState(false);

  const toggleThemeMode = (event: MouseEvent<HTMLButtonElement>) => {
    if (themeAnimating) {
      return;
    }

    const next = themeMode === 'dark' ? 'light' : 'dark';
    const rect = event.currentTarget.getBoundingClientRect();
    const originX = rect.left + rect.width / 2;
    const originY = rect.top + rect.height / 2;

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
