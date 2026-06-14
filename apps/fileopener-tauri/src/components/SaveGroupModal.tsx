import { modalBackdropStyle, modalSurfaceStyle } from './modalStyles';

type SaveGroupModalProps = {
  groupName: string;
  onGroupNameChange: (value: string) => void;
  onCancel: () => void;
  onSave: () => void;
};

export function SaveGroupModal({
  groupName,
  onGroupNameChange,
  onCancel,
  onSave
}: SaveGroupModalProps) {
  return (
    <div className="modal-backdrop" style={modalBackdropStyle}>
      <div className="modal" style={modalSurfaceStyle}>
        <h3>保存文件组</h3>
        <input
          autoFocus
          value={groupName}
          onChange={(event) => onGroupNameChange(event.target.value)}
          placeholder="请输入文件组名称"
          onKeyDown={(event) => {
            if (event.key === 'Enter') {
              onSave();
            }
          }}
        />
        <div className="modal-actions">
          <button className="btn btn-secondary" onClick={onCancel}>取消</button>
          <button className="btn btn-success" onClick={onSave}>保存</button>
        </div>
      </div>
    </div>
  );
}
