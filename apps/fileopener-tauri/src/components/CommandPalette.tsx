import { useEffect, useMemo, useRef, useState } from 'react';

import { filterCommandItems, type CommandPaletteSearchItem } from '../command-palette-utils';

export type CommandPaletteItem = CommandPaletteSearchItem & {
  id: string;
  shortcut?: string;
  disabled?: boolean;
  tone?: 'default' | 'danger' | 'success';
  onRun: () => void;
};

type CommandPaletteProps = {
  items: CommandPaletteItem[];
  onClose: () => void;
};

export function CommandPalette({ items, onClose }: CommandPaletteProps) {
  const [query, setQuery] = useState('');
  const [activeIndex, setActiveIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const filteredItems = useMemo(() => filterCommandItems(items, query), [items, query]);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const runCommand = (item: CommandPaletteItem) => {
    if (item.disabled) {
      return;
    }
    onClose();
    item.onRun();
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
    if (event.key === 'Escape') {
      event.preventDefault();
      onClose();
      return;
    }

    if (filteredItems.length === 0) {
      return;
    }

    if (event.key === 'ArrowDown') {
      event.preventDefault();
      setActiveIndex((previous) => (previous + 1) % filteredItems.length);
      return;
    }

    if (event.key === 'ArrowUp') {
      event.preventDefault();
      setActiveIndex((previous) => (previous - 1 + filteredItems.length) % filteredItems.length);
      return;
    }

    if (event.key === 'Enter') {
      event.preventDefault();
      runCommand(filteredItems[Math.min(activeIndex, filteredItems.length - 1)]);
    }
  };

  return (
    <div className="command-backdrop" onMouseDown={onClose}>
      <div
        className="command-palette"
        role="dialog"
        aria-modal="true"
        aria-label="指令中心"
        onKeyDown={handleKeyDown}
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="command-orb" aria-hidden="true" />
        <div className="command-header">
          <span className="command-kicker">Command Center</span>
          <strong>想做什么，直接搜</strong>
        </div>
        <div className="command-search-shell">
          <span aria-hidden="true">⌘</span>
          <input
            ref={inputRef}
            value={query}
            onChange={(event) => {
              setQuery(event.target.value);
              setActiveIndex(0);
            }}
            placeholder="搜索操作，例如：打开、导入、主题..."
          />
          <kbd>Esc</kbd>
        </div>

        <div className="command-list" role="listbox">
          {filteredItems.length === 0 ? (
            <div className="command-empty">没有匹配的操作</div>
          ) : (
            filteredItems.map((item, index) => (
              <button
                className={`command-item${index === activeIndex ? ' is-active' : ''}${
                  item.disabled ? ' is-disabled' : ''
                }${item.tone ? ` tone-${item.tone}` : ''}`}
                disabled={item.disabled}
                key={item.id}
                role="option"
                type="button"
                aria-selected={index === activeIndex}
                onMouseEnter={() => setActiveIndex(index)}
                onClick={() => runCommand(item)}
              >
                <span className="command-item-mark" aria-hidden="true" />
                <span className="command-item-main">
                  <strong>{item.title}</strong>
                  <small>{item.description}</small>
                </span>
                {item.shortcut && <kbd>{item.shortcut}</kbd>}
              </button>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
