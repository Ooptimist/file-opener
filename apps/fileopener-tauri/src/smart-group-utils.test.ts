import { describe, it } from 'node:test';
import assert from 'node:assert/strict';

import { deriveSmartGroupSuggestions } from './smart-group-utils.js';

describe('smart group utils', () => {
  it('derives useful category suggestions from mixed files', () => {
    const suggestions = deriveSmartGroupSuggestions([
      'C:\\Work\\brief.pdf',
      'C:\\Work\\notes.md',
      'C:\\Work\\cover.png',
      'C:\\Work\\hero.jpg',
      'C:\\Work\\index.ts',
      'C:\\Work\\app.tsx',
      'C:\\Work\\lonely.exe'
    ]);

    assert.deepEqual(
      suggestions.map((suggestion) => suggestion.id),
      ['documents', 'images', 'code']
    );
    assert.equal(suggestions[0].files.length, 2);
    assert.equal(suggestions[1].files.length, 2);
    assert.equal(suggestions[2].files.length, 2);
  });

  it('returns no suggestions when there are no meaningful groups', () => {
    const suggestions = deriveSmartGroupSuggestions([
      'C:\\Work\\brief.pdf',
      'C:\\Work\\cover.png',
      'C:\\Work\\index.ts'
    ]);

    assert.deepEqual(suggestions, []);
  });
});
