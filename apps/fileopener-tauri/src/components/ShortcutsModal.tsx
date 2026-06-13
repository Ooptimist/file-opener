type ShortcutsModalProps = {
  onClose: () => void;
};

const SHORTCUTS = [
  ['Ctrl + K', '打开指令中心'],
  ['Ctrl + O', '选择文件'],
  ['Ctrl + S', '保存当前文件列表为文件组'],
  ['Ctrl + Enter', '打开当前文件列表'],
  ['Ctrl + Shift + C', '复制当前文件路径'],
  ['Esc', '关闭当前弹窗']
];

export function ShortcutsModal({ onClose }: ShortcutsModalProps) {
  return (
    <div className="modal-backdrop">
      <div className="modal">
        <h3>快捷键</h3>
        <div className="shortcut-list">
          {SHORTCUTS.map(([keys, label]) => (
            <div className="shortcut-item" key={keys}>
              <kbd>{keys}</kbd>
              <span>{label}</span>
            </div>
          ))}
        </div>
        <div className="modal-actions">
          <button className="btn btn-secondary" onClick={onClose}>关闭</button>
        </div>
      </div>
    </div>
  );
}
