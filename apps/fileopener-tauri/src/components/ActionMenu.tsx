import { useEffect, useRef, useState } from 'react';

export type ActionMenuItem = {
  label: string;
  onClick: () => void;
  disabled?: boolean;
  tone?: 'default' | 'danger';
  icon?: string;
};

type ActionMenuProps = {
  label?: string;
  title?: string;
  align?: 'left' | 'right';
  items: ActionMenuItem[];
};

export function ActionMenu({ label = '更多', title, align = 'right', items }: ActionMenuProps) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) {
      return undefined;
    }

    const handlePointerDown = (event: PointerEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) {
        setOpen(false);
      }
    };

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setOpen(false);
      }
    };

    window.addEventListener('pointerdown', handlePointerDown);
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('pointerdown', handlePointerDown);
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [open]);

  return (
    <div className="action-menu" ref={rootRef}>
      <button
        className="mini-btn action-menu-trigger"
        type="button"
        aria-haspopup="menu"
        aria-expanded={open}
        title={title ?? label}
        onClick={() => setOpen((previous) => !previous)}
      >
        {label}
      </button>

      {open && (
        <div className={`action-menu-panel action-menu-${align}`} role="menu">
          {items.map((item) => (
            <button
              className={`action-menu-item${item.tone === 'danger' ? ' danger' : ''}`}
              disabled={item.disabled}
              key={item.label}
              role="menuitem"
              type="button"
              onClick={() => {
                if (item.disabled) {
                  return;
                }
                setOpen(false);
                item.onClick();
              }}
            >
              {item.icon && <img src={item.icon} alt="" />}
              <span>{item.label}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
