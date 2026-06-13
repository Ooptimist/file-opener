import { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { getActionMenuPosition, type ActionMenuAlign } from '../action-menu-utils';

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
  align?: ActionMenuAlign;
  items: ActionMenuItem[];
};

export function ActionMenu({ label = '更多', title, align = 'right', items }: ActionMenuProps) {
  const [open, setOpen] = useState(false);
  const [menuPosition, setMenuPosition] = useState({ left: 0, top: 0 });
  const menuRef = useRef<HTMLDivElement>(null);
  const rootRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);

  const updateMenuPosition = useCallback(() => {
    const trigger = triggerRef.current;
    if (!trigger) {
      return;
    }

    const rect = trigger.getBoundingClientRect();
    setMenuPosition(getActionMenuPosition({
      align,
      menuHeight: menuRef.current?.offsetHeight ?? 184,
      menuWidth: menuRef.current?.offsetWidth ?? 150,
      triggerRect: {
        bottom: rect.bottom,
        left: rect.left,
        right: rect.right
      },
      triggerTop: rect.top,
      viewportHeight: window.innerHeight,
      viewportWidth: window.innerWidth
    }));
  }, [align]);

  useLayoutEffect(() => {
    if (open) {
      updateMenuPosition();
    }
  }, [open, updateMenuPosition]);

  useEffect(() => {
    if (!open) {
      return undefined;
    }

    const handlePointerDown = (event: PointerEvent) => {
      const target = event.target as Node;
      if (!rootRef.current?.contains(target) && !menuRef.current?.contains(target)) {
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
    window.addEventListener('resize', updateMenuPosition);
    window.addEventListener('scroll', updateMenuPosition, true);
    return () => {
      window.removeEventListener('pointerdown', handlePointerDown);
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('resize', updateMenuPosition);
      window.removeEventListener('scroll', updateMenuPosition, true);
    };
  }, [open, updateMenuPosition]);

  return (
    <div className="action-menu" ref={rootRef}>
      <button
        className="mini-btn action-menu-trigger"
        type="button"
        aria-haspopup="menu"
        aria-expanded={open}
        ref={triggerRef}
        title={title ?? label}
        onClick={() => {
          if (!open) {
            updateMenuPosition();
          }
          setOpen((previous) => !previous);
        }}
      >
        {label}
      </button>

      {open && createPortal(
        <div
          className={`action-menu-panel action-menu-${align}`}
          ref={menuRef}
          role="menu"
          style={{
            backdropFilter: 'blur(34px) saturate(170%)',
            WebkitBackdropFilter: 'blur(34px) saturate(170%)',
            left: `${menuPosition.left}px`,
            top: `${menuPosition.top}px`
          }}
        >
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
        </div>,
        document.body
      )}
    </div>
  );
}
