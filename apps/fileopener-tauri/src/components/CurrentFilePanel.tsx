import { ActionMenu } from './ActionMenu';
import { getFileIcon, getFileName, normalizeIdentity } from '../file-utils';
import type { SmartGroupSuggestion } from '../smart-group-utils';

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
  smartSuggestions: SmartGroupSuggestion[];
  onFileKeywordChange: (value: string) => void;
  onSelectFiles: () => void;
  onSaveGroupClick: () => void;
  onSelectAllFilteredFiles: () => void;
  onInvertFilteredSelection: () => void;
  onClearSelection: () => void;
  onCopySelectedPaths: () => void;
  onClearFileList: () => void;
  onToggleFileChecked: (file: string) => void;
  onRemoveSelectedFiles: () => void;
  onOpenSelectedFiles: () => void;
  onSelectSmartSuggestion: (suggestion: SmartGroupSuggestion) => void;
  onSaveSmartSuggestion: (suggestion: SmartGroupSuggestion) => void;
};

export function CurrentFilePanel({
  selectedFiles,
  checkedFiles,
  checkedCount,
  filteredFiles,
  fileKeyword,
  dragActive,
  smartSuggestions,
  onFileKeywordChange,
  onSelectFiles,
  onSaveGroupClick,
  onSelectAllFilteredFiles,
  onInvertFilteredSelection,
  onClearSelection,
  onCopySelectedPaths,
  onClearFileList,
  onToggleFileChecked,
  onRemoveSelectedFiles,
  onOpenSelectedFiles,
  onSelectSmartSuggestion,
  onSaveSmartSuggestion
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

      {smartSuggestions.length > 0 && (
        <div className="smart-suggestions" aria-label="智能分组建议">
          <div className="smart-suggestions-title">
            <span>智能建议</span>
            <small>根据当前文件类型自动生成</small>
          </div>
          <div className="smart-suggestion-list">
            {smartSuggestions.map((suggestion) => (
              <article className={`smart-suggestion accent-${suggestion.accent}`} key={suggestion.id}>
                <div>
                  <strong>{suggestion.title}</strong>
                  <span>{suggestion.count} 个文件 · {suggestion.description}</span>
                </div>
                <div className="smart-suggestion-actions">
                  <button className="mini-btn" type="button" onClick={() => onSelectSmartSuggestion(suggestion)}>
                    勾选
                  </button>
                  <button className="mini-btn" type="button" onClick={() => onSaveSmartSuggestion(suggestion)}>
                    保存为组
                  </button>
                </div>
              </article>
            ))}
          </div>
        </div>
      )}

      <div className="sub-toolbar">
        <input
          className="search-input"
          placeholder="筛选文件名或路径"
          value={fileKeyword}
          onChange={(event) => onFileKeywordChange(event.target.value)}
        />
        <div className="inline-actions">
          <button
            className="mini-btn"
            type="button"
            onClick={onSelectAllFilteredFiles}
            disabled={filteredFiles.length === 0}
          >
            全选筛选
          </button>
          <button
            className="mini-btn"
            type="button"
            onClick={onClearSelection}
            disabled={checkedCount === 0}
          >
            清空勾选
          </button>
          <ActionMenu
            items={[
              { label: '反选筛选', onClick: onInvertFilteredSelection, disabled: filteredFiles.length === 0 },
              { label: '复制路径', onClick: onCopySelectedPaths, disabled: selectedFiles.length === 0 },
              { label: '清空列表', onClick: onClearFileList, disabled: selectedFiles.length === 0 }
            ]}
          />
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
