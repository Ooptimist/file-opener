import { getFileIcon, getFileName, normalizeIdentity } from '../file-utils';

import iconOpen from '../assets/icons/fluent/open.png';
import iconRemove from '../assets/icons/fluent/remove.png';
import iconSaveGroup from '../assets/icons/fluent/save-group.png';
import iconSelectFiles from '../assets/icons/fluent/select-files.png';

type CurrentFilePanelProps = {
  selectedFiles: string[];
  checkedFiles: Set<string>;
  checkedCount: number;
  filteredFiles: string[];
  fileKeyword: string;
  dragActive: boolean;
  onFileKeywordChange: (value: string) => void;
  onSelectFiles: () => void;
  onSaveGroupClick: () => void;
  onSelectAllFilteredFiles: () => void;
  onInvertFilteredSelection: () => void;
  onClearSelection: () => void;
  onToggleFileChecked: (file: string) => void;
  onRemoveSelectedFiles: () => void;
  onOpenSelectedFiles: () => void;
};

export function CurrentFilePanel({
  selectedFiles,
  checkedFiles,
  checkedCount,
  filteredFiles,
  fileKeyword,
  dragActive,
  onFileKeywordChange,
  onSelectFiles,
  onSaveGroupClick,
  onSelectAllFilteredFiles,
  onInvertFilteredSelection,
  onClearSelection,
  onToggleFileChecked,
  onRemoveSelectedFiles,
  onOpenSelectedFiles
}: CurrentFilePanelProps) {
  return (
    <section className="panel panel-left">
      <div className="panel-title-row">
        <h2>当前文件列表</h2>
        <span>{selectedFiles.length} 个文件 / {checkedCount} 个已勾选</span>
      </div>

      <div className="toolbar toolbar-main">
        <button className="btn btn-primary" onClick={onSelectFiles}>
          <img src={iconSelectFiles} alt="" />
          选择文件
        </button>
        <button className="btn btn-success" onClick={onSaveGroupClick} disabled={selectedFiles.length === 0}>
          <img src={iconSaveGroup} alt="" />
          保存文件组
        </button>
      </div>

      <div className="sub-toolbar">
        <input
          className="search-input"
          placeholder="筛选文件名或路径"
          value={fileKeyword}
          onChange={(event) => onFileKeywordChange(event.target.value)}
        />
        <div className="inline-actions">
          <button className="mini-btn" onClick={onSelectAllFilteredFiles}>全选筛选</button>
          <button className="mini-btn" onClick={onInvertFilteredSelection}>反选筛选</button>
          <button className="mini-btn" onClick={onClearSelection}>清空勾选</button>
        </div>
      </div>

      <div className={`file-list ${dragActive ? 'drag-active' : ''}`}>
        {selectedFiles.length === 0 ? (
          <div className="empty-state">
            暂无文件
            <br />
            <br />
            点击“选择文件”或将文件拖拽到窗口
          </div>
        ) : filteredFiles.length === 0 ? (
          <div className="empty-state">没有匹配筛选条件的文件</div>
        ) : (
          filteredFiles.map((file) => {
            const key = normalizeIdentity(file);
            const checked = checkedFiles.has(key);
            return (
              <label className="file-item" key={key}>
                <span className="file-check-cell">
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={() => onToggleFileChecked(file)}
                  />
                </span>
                <span className="file-name">{getFileIcon(file)} {getFileName(file)}</span>
                <span className="file-path" title={file}>{file}</span>
              </label>
            );
          })
        )}
      </div>

      <div className="toolbar file-action-toolbar">
        <button className="btn btn-danger" onClick={onRemoveSelectedFiles} disabled={checkedCount === 0}>
          <img src={iconRemove} alt="" />
          移除选中
        </button>
        <button className="btn btn-success" onClick={onOpenSelectedFiles} disabled={selectedFiles.length === 0}>
          <img src={iconOpen} alt="" />
          打开文件
        </button>
      </div>
    </section>
  );
}
