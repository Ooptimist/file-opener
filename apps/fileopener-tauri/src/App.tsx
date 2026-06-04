import { type MouseEvent, useCallback, useEffect, useMemo, useState } from 'react';
import { getCurrentWindow } from '@tauri-apps/api/window';
import type { UnlistenFn } from '@tauri-apps/api/event';
import { open } from '@tauri-apps/plugin-dialog';
import './App.css';
import { tokens } from './design-tokens';
import { api } from './tauri-api';
import type { GroupStats, GroupsRecord } from './types';

import iconSelectFiles from './assets/icons/fluent/select-files.png';
import iconSaveGroup from './assets/icons/fluent/save-group.png';
import iconRemove from './assets/icons/fluent/remove.png';
import iconOpen from './assets/icons/fluent/open.png';
import iconExpand from './assets/icons/fluent/expand.png';
import iconCollapse from './assets/icons/fluent/collapse.png';
import iconEdit from './assets/icons/fluent/edit.png';
import iconFolder from './assets/icons/fluent/folder.png';

const FILE_ICONS: Record<string, string> = {
  '.txt': '📄',
  '.pdf': '📕',
  '.doc': '📘',
  '.docx': '📘',
  '.xls': '📗',
  '.xlsx': '📗',
  '.ppt': '📙',
  '.pptx': '📙',
  '.png': '🖼️',
  '.jpg': '🖼️',
  '.jpeg': '🖼️',
  '.gif': '🖼️',
  '.mp3': '🎵',
  '.mp4': '🎬',
  '.zip': '🗜️',
  '.rar': '🗜️',
  '.exe': '⚙️',
  '.py': '🐍',
  '.js': '📜',
  '.html': '🌐',
  '.css': '🎨'
};

const DEFAULT_FILE_ICON = '📁';

type StatusTone = 'neutral' | 'success' | 'danger';
type ThemeMode = 'dark' | 'light';

type ViewTransitionDocument = Document & {
  startViewTransition?: (callback: () => void) => {
    ready: Promise<void>;
    finished: Promise<void>;
  };
};


type StatusState = {
  message: string;
  tone: StatusTone;
};

type EditModalState = {
  open: boolean;
  originalName: string;
  name: string;
  files: string[];
  checked: Set<string>;
};

const EMPTY_EDIT_MODAL: EditModalState = {
  open: false,
  originalName: '',
  name: '',
  files: [],
  checked: new Set()
};

function getInitialTheme(): ThemeMode {
  const savedTheme = window.localStorage.getItem('fileopener-theme');
  return savedTheme === 'light' ? 'light' : 'dark';
}

function getThemeRevealRadius(x: number, y: number) {
  return Math.hypot(Math.max(x, window.innerWidth - x), Math.max(y, window.innerHeight - y));
}

function getFileName(path: string) {
  const normalized = path.replace(/\//g, '\\');
  const idx = normalized.lastIndexOf('\\');
  return idx >= 0 ? normalized.slice(idx + 1) : normalized;
}

function getFileIcon(path: string) {
  const name = getFileName(path);
  const idx = name.lastIndexOf('.');
  if (idx < 0) {
    return DEFAULT_FILE_ICON;
  }
  const ext = name.slice(idx).toLowerCase();
  return FILE_ICONS[ext] ?? DEFAULT_FILE_ICON;
}

function normalizeIdentity(path: string) {
  return path.trim().replace(/\//g, '\\').toLowerCase();
}

function mergeAndDedupeFiles(current: string[], incoming: string[]) {
  const seen = new Set(current.map((item) => normalizeIdentity(item)));
  const out = [...current];

  for (const file of incoming) {
    const normalized = file.trim();
    if (!normalized) {
      continue;
    }
    const key = normalizeIdentity(normalized);
    if (seen.has(key)) {
      continue;
    }
    seen.add(key);
    out.push(normalized);
  }

  return out;
}

function App() {
  const [themeMode, setThemeMode] = useState<ThemeMode>(getInitialTheme);
  const [themeAnimating, setThemeAnimating] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [checkedFiles, setCheckedFiles] = useState<Set<string>>(new Set());
  const [groups, setGroups] = useState<GroupsRecord>({});
  const [groupStats, setGroupStats] = useState<Record<string, GroupStats>>({});
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set());

  const [status, setStatus] = useState<StatusState>({
    message: '初始化中...',
    tone: 'neutral'
  });

  const [fileKeyword, setFileKeyword] = useState('');
  const [groupKeyword, setGroupKeyword] = useState('');
  const [dragActive, setDragActive] = useState(false);

  const [saveModalOpen, setSaveModalOpen] = useState(false);
  const [saveGroupName, setSaveGroupName] = useState('');

  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);

  const [editModal, setEditModal] = useState<EditModalState>(EMPTY_EDIT_MODAL);

  const notify = useCallback((message: string, tone: StatusTone = 'neutral') => {
    setStatus({ message, tone });
  }, []);

  const toggleThemeMode = (event: MouseEvent<HTMLButtonElement>) => {
    if (themeAnimating) {
      return;
    }

    const next = themeMode === 'dark' ? 'light' : 'dark';
    const rect = event.currentTarget.getBoundingClientRect();
    const originX = rect.left + rect.width / 2;
    const originY = rect.top + rect.height / 2;

    const applyTheme = () => {
      setThemeMode(next);
      window.localStorage.setItem('fileopener-theme', next);
    };

    const viewTransitionDocument = document as ViewTransitionDocument;
    if (!viewTransitionDocument.startViewTransition) {
      applyTheme();
      return;
    }

    setThemeAnimating(true);
    const transition = viewTransitionDocument.startViewTransition(applyTheme);

    transition.ready
      .then(() => {
        const radius = getThemeRevealRadius(originX, originY);
        document.documentElement.animate(
          {
            clipPath: [
              `circle(0px at ${originX}px ${originY}px)`,
              `circle(${radius}px at ${originX}px ${originY}px)`
            ]
          },
          {
            duration: 620,
            easing: 'cubic-bezier(0.22, 1, 0.36, 1)',
            pseudoElement: '::view-transition-new(root)'
          }
        );
      })
      .catch(() => undefined);

    transition.finished.finally(() => {
      setThemeAnimating(false);
    });
  };

  const filteredFiles = useMemo(() => {
    const keyword = fileKeyword.trim().toLowerCase();
    if (!keyword) {
      return selectedFiles;
    }

    return selectedFiles.filter((file) => {
      const fileName = getFileName(file).toLowerCase();
      return fileName.includes(keyword) || file.toLowerCase().includes(keyword);
    });
  }, [selectedFiles, fileKeyword]);

  const filteredGroupEntries = useMemo(() => {
    const keyword = groupKeyword.trim().toLowerCase();
    const entries = Object.entries(groups);
    if (!keyword) {
      return entries;
    }

    return entries.filter(([name, files]) => {
      if (name.toLowerCase().includes(keyword)) {
        return true;
      }
      return files.some((file) => file.toLowerCase().includes(keyword));
    });
  }, [groups, groupKeyword]);

  const checkedCount = checkedFiles.size;

  const filesToOpen = useMemo(() => {
    if (checkedFiles.size === 0) {
      return selectedFiles;
    }
    return selectedFiles.filter((file) => checkedFiles.has(normalizeIdentity(file)));
  }, [selectedFiles, checkedFiles]);

  const refreshGroupStats = useCallback(async (nextGroups: GroupsRecord) => {
    const names = Object.keys(nextGroups);
    if (names.length === 0) {
      setGroupStats({});
      return;
    }

    const pairs = await Promise.all(
      names.map(async (name) => {
        const stats = await api.getGroupStats(name);
        return [name, stats] as const;
      })
    );

    setGroupStats(Object.fromEntries(pairs));
  }, []);

  const refreshGroups = useCallback(async () => {
    const nextGroups = await api.loadGroups();
    setGroups(nextGroups);
    await refreshGroupStats(nextGroups);
  }, [refreshGroupStats]);

  const addFilesToSelection = useCallback((files: string[]) => {
    if (files.length === 0) {
      return;
    }

    setSelectedFiles((previous) => mergeAndDedupeFiles(previous, files));
  }, []);

  useEffect(() => {
    let mounted = true;
    let dragDropUnlisten: UnlistenFn | undefined;

    const init = async () => {
      try {
        const migration = await api.migrateLegacyGroups();
        const nextGroups = await api.loadGroups();

        if (!mounted) {
          return;
        }

        setGroups(nextGroups);
        await refreshGroupStats(nextGroups);

        if (migration.migrated) {
          notify(`已从旧版本迁移数据: ${migration.source ?? '未知路径'}`, 'success');
        } else {
          notify('就绪', 'success');
        }
      } catch (error) {
        console.error(error);
        if (mounted) {
          notify(`初始化失败: ${String(error)}`, 'danger');
        }
      }
    };

    const bindDrop = async () => {
      try {
        dragDropUnlisten = await getCurrentWindow().onDragDropEvent((event) => {
          if (event.payload.type === 'enter' || event.payload.type === 'over') {
            setDragActive(true);
            return;
          }

          if (event.payload.type === 'leave') {
            setDragActive(false);
            return;
          }

          if (event.payload.type === 'drop') {
            setDragActive(false);
            addFilesToSelection(event.payload.paths);
            notify(`已拖拽添加 ${event.payload.paths.length} 个文件`, 'success');
          }
        });
      } catch (error) {
        console.error('绑定拖拽监听失败', error);
      }
    };

    void init();
    void bindDrop();

    return () => {
      mounted = false;
      if (dragDropUnlisten) {
        dragDropUnlisten();
      }
    };
  }, [addFilesToSelection, notify, refreshGroupStats]);

  const handleSelectFiles = async () => {
    try {
      const result = await open({
        multiple: true,
        directory: false,
        title: '选择文件'
      });

      if (!result) {
        return;
      }

      const files = Array.isArray(result) ? result : [result];
      addFilesToSelection(files);
      notify(`已添加 ${files.length} 个文件`, 'success');
    } catch (error) {
      console.error(error);
      notify(`选择文件失败: ${String(error)}`, 'danger');
    }
  };

  const handleToggleFileChecked = (file: string) => {
    const key = normalizeIdentity(file);
    setCheckedFiles((previous) => {
      const next = new Set(previous);
      if (next.has(key)) {
        next.delete(key);
      } else {
        next.add(key);
      }
      return next;
    });
  };

  const selectAllFilteredFiles = () => {
    if (filteredFiles.length === 0) {
      return;
    }

    setCheckedFiles((previous) => {
      const next = new Set(previous);
      for (const file of filteredFiles) {
        next.add(normalizeIdentity(file));
      }
      return next;
    });
    notify(`已选中筛选结果 ${filteredFiles.length} 个文件`, 'success');
  };

  const invertFilteredSelection = () => {
    if (filteredFiles.length === 0) {
      return;
    }

    setCheckedFiles((previous) => {
      const next = new Set(previous);
      for (const file of filteredFiles) {
        const key = normalizeIdentity(file);
        if (next.has(key)) {
          next.delete(key);
        } else {
          next.add(key);
        }
      }
      return next;
    });
    notify('已反选筛选结果', 'neutral');
  };

  const clearSelection = () => {
    if (checkedFiles.size === 0) {
      return;
    }

    setCheckedFiles(new Set());
    notify('已清空勾选', 'neutral');
  };

  const handleRemoveSelectedFiles = () => {
    if (checkedFiles.size === 0) {
      notify('请先勾选要移除的文件', 'neutral');
      return;
    }

    setSelectedFiles((previous) => previous.filter((file) => !checkedFiles.has(normalizeIdentity(file))));
    setCheckedFiles(new Set());
    notify('已移除选中文件', 'success');
  };

  const handleOpenSelectedFiles = async () => {
    if (filesToOpen.length === 0) {
      notify('没有可打开的文件', 'neutral');
      return;
    }

    try {
      const result = await api.openFiles(filesToOpen);
      if (result.failedFiles.length > 0) {
        notify(`成功打开 ${result.successCount} 个文件，失败 ${result.failedFiles.length} 个`, 'danger');
      } else {
        notify(`成功打开 ${result.successCount} 个文件`, 'success');
      }
    } catch (error) {
      console.error(error);
      notify(`打开文件失败: ${String(error)}`, 'danger');
    }
  };

  const handleSaveGroup = async () => {
    if (selectedFiles.length === 0) {
      notify('当前没有可保存的文件', 'neutral');
      return;
    }

    const name = saveGroupName.trim();
    if (!name) {
      notify('请输入文件组名称', 'neutral');
      return;
    }

    try {
      await api.saveGroup(name, selectedFiles);
      setSaveModalOpen(false);
      setSaveGroupName('');
      await refreshGroups();
      notify(`文件组“${name}”已保存`, 'success');
    } catch (error) {
      console.error(error);
      notify(`保存文件组失败: ${String(error)}`, 'danger');
    }
  };

  const handleToggleGroup = (name: string) => {
    setExpandedGroups((previous) => {
      const next = new Set(previous);
      if (next.has(name)) {
        next.delete(name);
      } else {
        next.add(name);
      }
      return next;
    });
  };

  const expandAllVisibleGroups = () => {
    setExpandedGroups(new Set(filteredGroupEntries.map(([name]) => name)));
  };

  const collapseAllGroups = () => {
    setExpandedGroups(new Set());
  };

  const handleOpenGroup = async (name: string) => {
    const files = groups[name] ?? [];
    if (files.length === 0) {
      notify('该文件组没有文件', 'neutral');
      return;
    }

    try {
      const result = await api.openFiles(files);
      if (result.failedFiles.length > 0) {
        notify(`成功打开 ${result.successCount} 个文件，失败 ${result.failedFiles.length} 个`, 'danger');
      } else {
        notify(`成功打开 ${result.successCount} 个文件`, 'success');
      }
    } catch (error) {
      console.error(error);
      notify(`打开文件组失败: ${String(error)}`, 'danger');
    }
  };

  const handleDeleteGroup = async () => {
    if (!deleteTarget) {
      return;
    }

    try {
      await api.deleteGroup(deleteTarget);
      setDeleteTarget(null);
      await refreshGroups();
      notify(`文件组“${deleteTarget}”已删除`, 'success');
    } catch (error) {
      console.error(error);
      notify(`删除文件组失败: ${String(error)}`, 'danger');
    }
  };

  const openEditModal = (name: string) => {
    const files = groups[name] ?? [];
    setEditModal({
      open: true,
      originalName: name,
      name,
      files: [...files],
      checked: new Set()
    });
  };

  const handleEditAddFiles = async () => {
    try {
      const result = await open({
        multiple: true,
        directory: false,
        title: '添加文件到分组'
      });

      if (!result) {
        return;
      }

      const files = Array.isArray(result) ? result : [result];
      setEditModal((previous) => ({
        ...previous,
        files: mergeAndDedupeFiles(previous.files, files)
      }));
    } catch (error) {
      console.error(error);
      notify(`添加文件失败: ${String(error)}`, 'danger');
    }
  };

  const handleEditToggleFile = (file: string) => {
    const key = normalizeIdentity(file);
    setEditModal((previous) => {
      const next = new Set(previous.checked);
      if (next.has(key)) {
        next.delete(key);
      } else {
        next.add(key);
      }
      return {
        ...previous,
        checked: next
      };
    });
  };

  const handleEditRemoveSelected = () => {
    setEditModal((previous) => ({
      ...previous,
      files: previous.files.filter((file) => !previous.checked.has(normalizeIdentity(file))),
      checked: new Set()
    }));
  };

  const handleEditSave = async () => {
    const nextName = editModal.name.trim();
    if (!nextName) {
      notify('文件组名称不能为空', 'neutral');
      return;
    }

    try {
      if (nextName !== editModal.originalName) {
        await api.renameGroup(editModal.originalName, nextName);
      }
      await api.updateGroupFiles(nextName, editModal.files);
      setEditModal(EMPTY_EDIT_MODAL);
      await refreshGroups();
      notify(`文件组“${nextName}”已更新`, 'success');
    } catch (error) {
      console.error(error);
      notify(`更新文件组失败: ${String(error)}`, 'danger');
    }
  };

  return (
    <div
      className={`app theme-${themeMode}`}
      style={{
        fontFamily: tokens.font.family,
        ['--primary' as string]: tokens.colors.primary,
        ['--success' as string]: tokens.colors.success,
        ['--danger' as string]: tokens.colors.danger
      }}
    >
      <header className="app-header">
        <div className="title-wrap">
          <div className="title-line">
            <h1>文件批量打开工具</h1>
            <button
              className={`theme-toggle theme-toggle-${themeMode}${
                themeAnimating ? ' theme-toggle-animating' : ''
              }`}
              type="button"
              onClick={toggleThemeMode}
              disabled={themeAnimating}
              aria-label={themeMode === 'dark' ? '切换到白天模式' : '切换到黑夜模式'}
              title={themeMode === 'dark' ? '切换到白天模式' : '切换到黑夜模式'}
            >
              <span className="theme-toggle-thumb" aria-hidden="true">
                <span className="theme-icon theme-icon-sun" />
                <span className="theme-icon theme-icon-moon" />
              </span>
              <span>{themeMode === 'dark' ? '黑夜' : '白天'}</span>
            </button>
          </div>
          <p>拖拽、分组、批量打开，一次完成</p>
        </div>
        <div className={`status-chip status-${status.tone}`} title={status.message}>
          {status.message}
        </div>
      </header>

      <main className="app-main">
        <section className="panel panel-left">
          <div className="panel-title-row">
            <h2>当前文件列表</h2>
            <span>{selectedFiles.length} 个文件 / {checkedCount} 个已勾选</span>
          </div>

          <div className="toolbar toolbar-main">
            <button className="btn btn-primary" onClick={handleSelectFiles}>
              <img src={iconSelectFiles} alt="" />
              选择文件
            </button>
            <button className="btn btn-success" onClick={() => setSaveModalOpen(true)}>
              <img src={iconSaveGroup} alt="" />
              保存文件组
            </button>
          </div>

          <div className="sub-toolbar">
            <input
              className="search-input"
              placeholder="筛选文件名或路径"
              value={fileKeyword}
              onChange={(event) => setFileKeyword(event.target.value)}
            />
            <div className="inline-actions">
              <button className="mini-btn" onClick={selectAllFilteredFiles}>全选筛选</button>
              <button className="mini-btn" onClick={invertFilteredSelection}>反选筛选</button>
              <button className="mini-btn" onClick={clearSelection}>清空勾选</button>
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
                        onChange={() => handleToggleFileChecked(file)}
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
            <button className="btn btn-danger" onClick={handleRemoveSelectedFiles}>
              <img src={iconRemove} alt="" />
              移除选中
            </button>
            <button className="btn btn-success" onClick={handleOpenSelectedFiles}>
              <img src={iconOpen} alt="" />
              打开文件
            </button>
          </div>
        </section>

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
              onChange={(event) => setGroupKeyword(event.target.value)}
            />
            <div className="inline-actions">
              <button className="mini-btn" onClick={expandAllVisibleGroups}>展开全部</button>
              <button className="mini-btn" onClick={collapseAllGroups}>折叠全部</button>
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
                      <button className="icon-btn" onClick={() => handleToggleGroup(name)}>
                        <img src={expanded ? iconCollapse : iconExpand} alt="" />
                      </button>

                      <div className="group-main">
                        <div className="group-name-row">
                          <img src={iconFolder} alt="" />
                          <strong>{name}</strong>
                        </div>
                        <div className="group-count">存在 {stats.existing} / 总计 {stats.total}</div>
                      </div>

                      <div className="group-actions">
                        <button className="btn btn-xs btn-success" onClick={() => handleOpenGroup(name)}>
                          <img src={iconOpen} alt="" />
                          打开
                        </button>
                        <button className="btn btn-xs btn-secondary" onClick={() => openEditModal(name)}>
                          <img src={iconEdit} alt="" />
                          编辑
                        </button>
                        <button className="btn btn-xs btn-danger" onClick={() => setDeleteTarget(name)}>
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
      </main>

      {saveModalOpen && (
        <div className="modal-backdrop">
          <div className="modal">
            <h3>保存文件组</h3>
            <input
              autoFocus
              value={saveGroupName}
              onChange={(event) => setSaveGroupName(event.target.value)}
              placeholder="请输入文件组名称"
              onKeyDown={(event) => {
                if (event.key === 'Enter') {
                  void handleSaveGroup();
                }
              }}
            />
            <div className="modal-actions">
              <button className="btn btn-secondary" onClick={() => setSaveModalOpen(false)}>取消</button>
              <button className="btn btn-success" onClick={handleSaveGroup}>保存</button>
            </div>
          </div>
        </div>
      )}

      {deleteTarget && (
        <div className="modal-backdrop">
          <div className="modal">
            <h3>确认删除</h3>
            <p>确定要删除文件组“{deleteTarget}”吗？</p>
            <div className="modal-actions">
              <button className="btn btn-secondary" onClick={() => setDeleteTarget(null)}>取消</button>
              <button className="btn btn-danger" onClick={handleDeleteGroup}>删除</button>
            </div>
          </div>
        </div>
      )}

      {editModal.open && (
        <div className="modal-backdrop">
          <div className="modal modal-large">
            <h3>编辑文件组</h3>
            <input
              autoFocus
              value={editModal.name}
              onChange={(event) =>
                setEditModal((previous) => ({
                  ...previous,
                  name: event.target.value
                }))
              }
              placeholder="文件组名称"
            />

            <div className="toolbar toolbar-compact">
              <button className="btn btn-primary" onClick={handleEditAddFiles}>
                <img src={iconSelectFiles} alt="" />
                添加文件
              </button>
              <button className="btn btn-danger" onClick={handleEditRemoveSelected}>
                <img src={iconRemove} alt="" />
                删除选中
              </button>
            </div>

            <div className="file-list file-list-edit">
              {editModal.files.length === 0 ? (
                <div className="empty-state">该分组暂无文件</div>
              ) : (
                editModal.files.map((file) => {
                  const key = normalizeIdentity(file);
                  const checked = editModal.checked.has(key);
                  return (
                    <label className="file-item" key={key}>
                      <span className="file-check-cell">
                        <input
                          type="checkbox"
                          checked={checked}
                          onChange={() => handleEditToggleFile(file)}
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
              <button className="btn btn-secondary" onClick={() => setEditModal(EMPTY_EDIT_MODAL)}>取消</button>
              <button className="btn btn-success" onClick={handleEditSave}>保存</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
