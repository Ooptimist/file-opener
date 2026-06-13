import type { ThemeMode } from './types.js';

export function getInitialThemeMode(savedTheme: string | null): ThemeMode {
  return savedTheme === 'light' ? 'light' : 'dark';
}

export function toNativeWindowTheme(themeMode: ThemeMode): ThemeMode {
  return themeMode;
}
