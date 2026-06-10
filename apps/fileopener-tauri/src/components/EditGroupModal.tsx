import { getFileIcon, getFileName, normalizeIdentity } from '../file-utils';
import type { EditModalState } from '../types';

import iconRemove from '../assets/icons/fluent/remove.png';
import iconSelectFiles from '../assets/icons/fluent/select-files.png';

type EditGroupModalProps = {
  modal: EditModalState;
  onNameChange: (value: string) => void;
  onAddFiles: () => void;
  onRemoveSelected: () => void;
  onToggleFile: (file: string) => void;
  onCancel: () => void;
  onSave: () => void;
};

export function EditGroupModal({
  modal,
  onNameChange,
  onAddFiles,
  onRemoveSelected,
  onToggleFile,
  onCancel,
  onSave
}: EditGroupModalProps) {
  return (
    <div className="modal-backdrop">
      <div className="modal modal-large">
        <h3>编辑文件组</h3>
        <input
          autoFocus
          value={modal.name}
          onChange={(event) => onNameChange(event.target.value)}
          placeholder="文件组名称"
        />

        <div className="toolbar toolbar-compact">
          <button className="btn btn-primary" onClick={onAddFiles}>
            <img src={iconSelectFiles} alt="" />
            添加文件
          </button>
          <button className="btn btn-danger" onClick={onRemoveSelected} disabled={modal.checked.size === 0}>
            <img src={iconRemove} alt="" />
            删除选中
          </button>
        </div>

        <div className="file-list file-list-edit">
          {modal.files.length === 0 ? (
            <div className="empty-state">该分组暂无文件</div>
          ) : (
            modal.files.map((file) => {
              const key = normalizeIdentity(file);
              const checked = modal.checked.has(key);
              return (
                <label className="file-item" key={key}>
                  <span className="file-check-cell">
                    <input
                      type="checkbox"
                      checked={checked}
                      onChange={() => onToggleFile(file)}
                    />
                  </span>
                  <span className="file-name">{getFileIcon(file)} {getFileName(file)}</span>
                  <span className="file-path" title={file}>{file}</span>
                </label>
              );
            })
          )}
        </div>

        <div className="modal-actions">
          <button className="btn btn-secondary" onClick={onCancel}>取消</button>
          <button className="btn btn-success" onClick={onSave}>保存</button>
        </div>
      </div>
    </div>
  );
}
