export type ActionMenuAlign = 'left' | 'right';

type TriggerRect = {
  bottom: number;
  left: number;
  right: number;
};

type ActionMenuPositionInput = {
  align: ActionMenuAlign;
  edgePadding?: number;
  gap?: number;
  menuHeight: number;
  menuWidth: number;
  triggerRect: TriggerRect;
  triggerTop: number;
  viewportHeight: number;
  viewportWidth: number;
};

export function getActionMenuPosition({
  align,
  edgePadding = 12,
  gap = 8,
  menuHeight,
  menuWidth,
  triggerRect,
  triggerTop,
  viewportHeight,
  viewportWidth
}: ActionMenuPositionInput) {
  const preferredLeft = align === 'right'
    ? triggerRect.right - menuWidth
    : triggerRect.left;
  const maxLeft = viewportWidth - menuWidth - edgePadding;
  const downwardTop = triggerRect.bottom + gap;
  const upwardTop = triggerTop - menuHeight - gap;
  const preferredTop = downwardTop + menuHeight > viewportHeight - edgePadding
    ? upwardTop
    : downwardTop;
  const maxTop = viewportHeight - menuHeight - edgePadding;

  return {
    left: Math.min(Math.max(preferredLeft, edgePadding), Math.max(edgePadding, maxLeft)),
    top: Math.min(Math.max(preferredTop, edgePadding), Math.max(edgePadding, maxTop))
  };
}
