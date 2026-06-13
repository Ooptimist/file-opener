import { describe, it } from 'node:test';
import assert from 'node:assert/strict';

import { filterCommandItems } from './command-palette-utils.js';

describe('command palette utils', () => {
  const items = [
    {
      id: 'select-files',
      title: '选择文件',
      description: '添加文件到当前列表',
      keywords: ['open', 'add']
    },
    {
      id: 'export-groups',
      title: '导出文件组',
      description: '保存 JSON 备份',
      keywords: ['backup', 'json']
    },
    {
      id: 'theme',
      title: '切换主题',
      description: '白天和黑夜模式',
      keywords: ['dark', 'light']
    }
  ];

  it('returns all commands when the query is blank', () => {
    assert.deepEqual(filterCommandItems(items, ' ').map((item) => item.id), [
      'select-files',
      'export-groups',
      'theme'
    ]);
  });

  it('matches command title, description, and keywords case-insensitively', () => {
    assert.deepEqual(filterCommandItems(items, 'JSON').map((item) => item.id), ['export-groups']);
    assert.deepEqual(filterCommandItems(items, 'dark').map((item) => item.id), ['theme']);
    assert.deepEqual(filterCommandItems(items, '当前').map((item) => item.id), ['select-files']);
  });
});
