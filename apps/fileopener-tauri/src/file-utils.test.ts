import { describe, it } from 'node:test';
import assert from 'node:assert/strict';

import {
  getFileIcon,
  getFileName,
  mergeAndDedupeFiles,
  normalizeIdentity
} from './file-utils.js';

describe('file utils', () => {
  it('gets file names from Windows and POSIX paths', () => {
    assert.equal(getFileName('C:\\Users\\Public\\Desktop\\demo.txt'), 'demo.txt');
    assert.equal(getFileName('/Users/demo/文件.pdf'), '文件.pdf');
  });

  it('normalizes identities for case-insensitive dedupe', () => {
    assert.equal(normalizeIdentity(' C:/Temp/Demo.TXT '), 'c:\\temp\\demo.txt');
  });

  it('merges non-empty files and removes duplicates while keeping order', () => {
    assert.deepEqual(
      mergeAndDedupeFiles(['C:\\Temp\\a.txt'], [' c:/temp/A.txt ', 'D:/Docs/b.pdf', '']),
      ['C:\\Temp\\a.txt', 'D:/Docs/b.pdf']
    );
  });

  it('returns a folder icon for unknown extensions', () => {
    assert.equal(getFileIcon('C:\\Temp\\archive.unknown'), '📁');
  });
});
