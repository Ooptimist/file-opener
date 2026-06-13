import { describe, it } from 'node:test';
import assert from 'node:assert/strict';

import { getFavoriteGroupEntries, pruneFavoriteGroups, toggleFavoriteGroup } from './favorite-group-utils.js';

describe('favorite group utils', () => {
  const groups = {
    docs: ['C:\\Work\\a.pdf'],
    code: ['C:\\Work\\app.ts'],
    images: ['C:\\Work\\cover.png']
  };

  it('toggles favorite group names while keeping order', () => {
    assert.deepEqual(toggleFavoriteGroup(['docs'], 'code'), ['docs', 'code']);
    assert.deepEqual(toggleFavoriteGroup(['docs', 'code'], 'docs'), ['code']);
  });

  it('removes favorite names that no longer exist', () => {
    assert.deepEqual(pruneFavoriteGroups(['missing', 'code', 'docs'], groups), ['code', 'docs']);
  });

  it('returns favorite entries in favorite order', () => {
    assert.deepEqual(getFavoriteGroupEntries(['images', 'docs'], groups), [
      ['images', ['C:\\Work\\cover.png']],
      ['docs', ['C:\\Work\\a.pdf']]
    ]);
  });
});
