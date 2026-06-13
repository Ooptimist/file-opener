import { describe, it } from 'node:test';
import assert from 'node:assert/strict';

import { getInitialThemeMode, toNativeWindowTheme } from './theme-utils.js';

describe('theme utils', () => {
  it('defaults to dark mode when there is no saved preference', () => {
    assert.equal(getInitialThemeMode(null), 'dark');
  });

  it('keeps light mode when saved explicitly', () => {
    assert.equal(getInitialThemeMode('light'), 'light');
  });

  it('maps app themes to native window themes', () => {
    assert.equal(toNativeWindowTheme('dark'), 'dark');
    assert.equal(toNativeWindowTheme('light'), 'light');
  });
});
