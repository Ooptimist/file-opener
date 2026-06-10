import { getFileIcon, getFileName, normalizeIdentity } from '../file-utils';
import type { GroupStats, GroupsRecord } from '../types';

import iconEdit from '../assets/icons/fluent/edit.png';
import iconExpand from '../assets/icons/fluent/expand.png';
import iconFolder from '../assets/icons/fluent/folder.png';
import iconOpen from '../assets/icons/fluent/open.png';
import iconRemove from '../assets/icons/fluent/remove.png';

type GroupPanelProps = {
  groups: GroupsRecord;
  groupStats: Record<string, GroupStats>;
  filteredGroupEntries: [string, string[]][];
  expandedGroups: Set<string>;
  groupKeyword: string;
  onGroupKeywordChange: (value: string) => void;
  onExpandAllVisibleGroups: () => void;
  onCollapseAllGroups: () => void;
  onToggleGroup: (name: string) => void;
  onOpenGroup: (name: string) => void;
  onEditGroup: (name: string) => void;
  onDeleteGroup: (name: string) => void;
};

export function GroupPanel({
  groups,
  groupStats,
  filteredGroupEntries,
  expandedGroups,
  groupKeyword,
  onGroupKeywordChange,
  onExpandAllVisibleGroups,
  onCollapseAllGroups,
  onToggleGroup,
  onOpenGroup,
  onEditGroup,
  onDeleteGroup
}: GroupPanelProps) {
  return (
    <section className="panel panel-right">
      <div className="panel-title-row">
        <h2>我的文件组</h2>
        <span>{Object.keys(groups).length} 个分组</span>
      </div>

      <div className="sub-toolbar">
        <input
          className="search-input"
          placeholder="筛选分组名或分组内路径"
          value={groupKeyword}
          onChange={(event) => onGroupKeywordChange(event.target.value)}
        />
        <div className="inline-actions">
          <button className="mini-btn" onClick={onExpandAllVisibleGroups}>展开全部</button>
          <button className="mini-btn" onClick={onCollapseAllGroups}>折叠全部</button>
        </div>
      </div>

      <div className="group-list">
        {Object.keys(groups).length === 0 ? (
          <div className="empty-state">
            暂无保存的文件组
            <br />
            <br />
            选择文件后点击“保存文件组”
          </div>
        ) : filteredGroupEntries.length === 0 ? (
          <div className="empty-state">没有匹配筛选条件的分组</div>
        ) : (
          filteredGroupEntries.map(([name, files]) => {
            const expanded = expandedGroups.has(name);
            const stats = groupStats[name] ?? { existing: 0, total: files.length };

            return (
              <article className="group-card" key={name}>
                <div className="group-head">
                  <button
                    className={`icon-btn ${expanded ? 'is-expanded' : 'is-collapsed'}`}
                    onClick={() => onToggleGroup(name)}
                    aria-label={expanded ? '收起文件组' : '展开文件组'}
                  >
                    <img src={iconExpand} alt="" />
                  </button>

                  <div className="group-main">
                    <div className="group-name-row">
                      <img src={iconFolder} alt="" />
                      <strong>{name}</strong>
                    </div>
                    <div className="group-count">存在 {stats.existing} / 总计 {stats.total}</div>
                  </div>

                  <div className="group-actions">
                    <button className="btn btn-xs btn-success" onClick={() => onOpenGroup(name)}>
                      <img src={iconOpen} alt="" />
                      打开
                    </button>
                    <button className="btn btn-xs btn-secondary" onClick={() => onEditGroup(name)}>
                      <img src={iconEdit} alt="" />
                      编辑
                    </button>
                    <button className="btn btn-xs btn-danger" onClick={() => onDeleteGroup(name)}>
                      <img src={iconRemove} alt="" />
                      删除
                    </button>
                  </div>
                </div>

                <div
                  className={`group-files-shell ${expanded ? 'expanded' : 'collapsed'}`}
                  aria-hidden={!expanded}
                >
                  <div className="group-files">
                    {files.map((file, index) => {
                      const fileKey = `${name}:${normalizeIdentity(file)}`;
                      return (
                        <div
                          className="group-file"
                          key={fileKey}
                          style={{ ['--group-file-index' as string]: index }}
                          title={file}
                        >
                          <span>{getFileIcon(file)} {getFileName(file)}</span>
                          <small>{file}</small>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </article>
            );
          })
        )}
      </div>
    </section>
  );
}
