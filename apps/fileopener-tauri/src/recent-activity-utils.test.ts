import { describe, it } from 'node:test';
import assert from 'node:assert/strict';

import { addRecentActivity, createRecentActivity } from './recent-activity-utils.js';

describe('recent activity utils', () => {
  it('does not create activities for empty file lists', () => {
    assert.equal(createRecentActivity('current', '空任务', []), null);
  });

  it('adds new activities to the top and limits history length', () => {
    const first = createRecentActivity('current', '当前列表', ['C:\\Work\\a.txt'], '2026-01-01T00:00:00.000Z');
    const second = createRecentActivity('group', '文件组 A', ['C:\\Work\\b.txt'], '2026-01-02T00:00:00.000Z');
    const third = createRecentActivity('group', '文件组 B', ['C:\\Work\\c.txt'], '2026-01-03T00:00:00.000Z');

    const history = addRecentActivity(third, addRecentActivity(second, addRecentActivity(first, [], 2), 2), 2);

    assert.deepEqual(history.map((item) => item.title), ['文件组 B', '文件组 A']);
  });

  it('moves duplicate activities to the top instead of keeping two copies', () => {
    const first = createRecentActivity('current', '旧名称', ['C:\\Work\\a.txt'], '2026-01-01T00:00:00.000Z');
    const duplicate = createRecentActivity('current', '新名称', ['c:/work/A.txt'], '2026-01-02T00:00:00.000Z');

    const history = addRecentActivity(duplicate, addRecentActivity(first, []));

    assert.equal(history.length, 1);
    assert.equal(history[0].title, '新名称');
  });
});
