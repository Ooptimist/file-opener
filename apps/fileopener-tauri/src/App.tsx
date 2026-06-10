import { useCallback, useEffect, useMemo, useState } from 'react';
import { getCurrentWindow } from '@tauri-apps/api/window';
import type { UnlistenFn } from '@tauri-apps/api/event';
import { open } from '@tauri-apps/plugin-dialog';
import './App.css';
import { CurrentFilePanel } from './components/CurrentFilePanel';
import { EditGroupModal } from './components/EditGroupModal';
import { GroupPanel } from './components/GroupPanel';
import { OpenFailuresModal } from './components/OpenFailuresModal';
import { SaveGroupModal } from './components/SaveGroupModal';
import { tokens } from './design-tokens';
import { getFileName, mergeAndDedupeFiles, normalizeIdentity } from './file-utils';
import { useThemeTransition } from './hooks/useThemeTransition';
import { api } from './tauri-api';
import type { EditModalState, GroupStats, GroupsRecord, StatusState, StatusTone } from './types';

const EMPTY_EDIT_MODAL: EditModalState = {
  open: false,
  originalName: '',
  name: '',
  files: [],
  checked: new Set()
};

function App() {
  const { themeMode, themeAnimating, toggleThemeMode } = useThemeTransition();
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

  const [failedFiles, setFailedFiles] = useState<string[]>([]);
  const [failuresModalOpen, setFailuresModalOpen] = useState(false);

  const notify = useCallback((message: string, tone: StatusTone = 'neutral') => {
    setStatus({ message, tone });
  }, []);

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

  const recordOpenResult = useCallback((successCount: number, nextFailedFiles: string[]) => {
    if (nextFailedFiles.length > 0) {
      setFailedFiles(nextFailedFiles);
      setFailuresModalOpen(true);
      notify(`成功打开 ${successCount} 个文件，失败 ${nextFailedFiles.length} 个`, 'danger');
      return;
    }

    setFailedFiles([]);
    setFailuresModalOpen(false);
    notify(`成功打开 ${successCount} 个文件`, 'success');
  }, [notify]);

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
      recordOpenResult(result.successCount, result.failedFiles);
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
      recordOpenResult(result.successCount, result.failedFiles);
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

  const handleEditNameChange = (name: string) => {
    setEditModal((previous) => ({
      ...previous,
      name
    }));
  };

  const copyFailedFiles = async () => {
    if (failedFiles.length === 0) {
      return;
    }

    try {
      await navigator.clipboard.writeText(failedFiles.join('\n'));
      notify('已复制失败文件路径', 'success');
    } catch (error) {
      console.error(error);
      notify(`复制失败路径失败: ${String(error)}`, 'danger');
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
        <div className="status-area">
          <div className={`status-chip status-${status.tone}`} title={status.message}>
            {status.message}
          </div>
          {failedFiles.length > 0 && (
            <button className="mini-btn status-action" onClick={() => setFailuresModalOpen(true)}>
              查看失败文件
            </button>
          )}
        </div>
      </header>

      <main className="app-main">
        <CurrentFilePanel
          selectedFiles={selectedFiles}
          checkedFiles={checkedFiles}
          checkedCount={checkedCount}
          filteredFiles={filteredFiles}
          fileKeyword={fileKeyword}
          dragActive={dragActive}
          onFileKeywordChange={setFileKeyword}
          onSelectFiles={handleSelectFiles}
          onSaveGroupClick={() => setSaveModalOpen(true)}
          onSelectAllFilteredFiles={selectAllFilteredFiles}
          onInvertFilteredSelection={invertFilteredSelection}
          onClearSelection={clearSelection}
          onToggleFileChecked={handleToggleFileChecked}
          onRemoveSelectedFiles={handleRemoveSelectedFiles}
          onOpenSelectedFiles={handleOpenSelectedFiles}
        />

        <GroupPanel
          groups={groups}
          groupStats={groupStats}
          filteredGroupEntries={filteredGroupEntries}
          expandedGroups={expandedGroups}
          groupKeyword={groupKeyword}
          onGroupKeywordChange={setGroupKeyword}
          onExpandAllVisibleGroups={expandAllVisibleGroups}
          onCollapseAllGroups={collapseAllGroups}
          onToggleGroup={handleToggleGroup}
          onOpenGroup={handleOpenGroup}
          onEditGroup={openEditModal}
          onDeleteGroup={setDeleteTarget}
        />
      </main>

      {saveModalOpen && (
        <SaveGroupModal
          groupName={saveGroupName}
          onGroupNameChange={setSaveGroupName}
          onCancel={() => setSaveModalOpen(false)}
          onSave={handleSaveGroup}
        />
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
        <EditGroupModal
          modal={editModal}
          onNameChange={handleEditNameChange}
          onAddFiles={handleEditAddFiles}
          onRemoveSelected={handleEditRemoveSelected}
          onToggleFile={handleEditToggleFile}
          onCancel={() => setEditModal(EMPTY_EDIT_MODAL)}
          onSave={handleEditSave}
        />
      )}

      {failuresModalOpen && failedFiles.length > 0 && (
        <OpenFailuresModal
          failedFiles={failedFiles}
          onCopy={copyFailedFiles}
          onClose={() => setFailuresModalOpen(false)}
        />
      )}
    </div>
  );
}

export default App;
