import { describe, it } from 'node:test';
import assert from 'node:assert/strict';

import { getActionMenuPosition } from './action-menu-utils.js';

describe('action menu utils', () => {
  it('positions a right-aligned menu from the viewport trigger rect', () => {
    assert.deepEqual(
      getActionMenuPosition({
        align: 'right',
        edgePadding: 12,
        gap: 8,
        menuHeight: 184,
        menuWidth: 150,
        triggerRect: { bottom: 392, left: 827, right: 885 },
        triggerTop: 354,
        viewportHeight: 900,
        viewportWidth: 920
      }),
      { left: 735, top: 400 }
    );
  });

  it('keeps the menu inside the viewport when the trigger is near the right edge', () => {
    assert.deepEqual(
      getActionMenuPosition({
        align: 'left',
        edgePadding: 12,
        gap: 8,
        menuHeight: 184,
        menuWidth: 240,
        triggerRect: { bottom: 460, left: 840, right: 898 },
        triggerTop: 422,
        viewportHeight: 900,
        viewportWidth: 920
      }),
      { left: 668, top: 468 }
    );
  });

  it('opens upward when the menu would overflow below the viewport', () => {
    assert.deepEqual(
      getActionMenuPosition({
        align: 'right',
        edgePadding: 12,
        gap: 8,
        menuHeight: 184,
        menuWidth: 150,
        triggerRect: { bottom: 468, left: 713, right: 771 },
        triggerTop: 430,
        viewportHeight: 496,
        viewportWidth: 830
      }),
      { left: 621, top: 238 }
    );
  });
});
