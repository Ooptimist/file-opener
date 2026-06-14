import { useCallback, useEffect, useMemo, useState } from 'react';
import { getCurrentWindow } from '@tauri-apps/api/window';
import type { UnlistenFn } from '@tauri-apps/api/event';
import { open, save } from '@tauri-apps/plugin-dialog';
import './App.css';
import { CommandPalette, type CommandPaletteItem } from './components/CommandPalette';
import { CurrentFilePanel } from './components/CurrentFilePanel';
import { EditGroupModal } from './components/EditGroupModal';
import { FavoriteGroupsDock } from './components/FavoriteGroupsDock';
import { GroupPanel } from './components/GroupPanel';
import { HealthCenterModal } from './components/HealthCenterModal';
import { OpenFailuresModal } from './components/OpenFailuresModal';
import { RecentActivityModal } from './components/RecentActivityModal';
import { SaveGroupModal } from './components/SaveGroupModal';
import { ShortcutsModal } from './components/ShortcutsModal';
import { WindowTitleBar } from './components/WindowTitleBar';
import { modalBackdropStyle, modalSurfaceStyle } from './components/modalStyles';
import { tokens } from './design-tokens';
import {
  getFavoriteGroupEntries,
  pruneFavoriteGroups,
  toggleFavoriteGroup
} from './favorite-group-utils';
import { getFileName, mergeAndDedupeFiles, normalizeIdentity } from './file-utils';
import { useThemeTransition } from './hooks/useThemeTransition';
import {
  addRecentActivity,
  createRecentActivity,
  type RecentActivityItem
} from './recent-activity-utils';
import { deriveSmartGroupSuggestions, type SmartGroupSuggestion } from './smart-group-utils';
import { api } from './tauri-api';
import type { EditModalState, GroupHealthReport, GroupStats, GroupsRecord, StatusState, StatusTone } from './types';

const EMPTY_EDIT_MODAL: EditModalState = {
  open: false,
  originalName: '',
  name: '',
  files: [],
  checked: new Set()
};

const RECENT_ACTIVITY_STORAGE_KEY = 'fileopener-recent-activity';
const FAVORITE_GROUPS_STORAGE_KEY = 'fileopener-favorite-groups';

function loadRecentActivities() {
  try {
    const raw = window.localStorage.getItem(RECENT_ACTIVITY_STORAGE_KEY);
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw) as RecentActivityItem[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function loadFavoriteGroups() {
  try {
    const raw = window.localStorage.getItem(FAVORITE_GROUPS_STORAGE_KEY);
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw) as string[];
    return Array.isArray(parsed) ? parsed.filter((item) => typeof item === 'string') : [];
  } catch {
    return [];
  }
}

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
  const [shortcutsModalOpen, setShortcutsModalOpen] = useState(false);
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const [healthModalOpen, setHealthModalOpen] = useState(false);
  const [healthLoading, setHealthLoading] = useState(false);
  const [healthReport, setHealthReport] = useState<GroupHealthReport | null>(null);
  const [recentModalOpen, setRecentModalOpen] = useState(false);
  const [recentActivities, setRecentActivities] = useState<RecentActivityItem[]>(loadRecentActivities);
  const [favoriteGroups, setFavoriteGroups] = useState<string[]>(loadFavoriteGroups);

  const notify = useCallback((message: string, tone: StatusTone = 'neutral') => {
    setStatus({ message, tone });
  }, []);

  useEffect(() => {
    window.localStorage.setItem(RECENT_ACTIVITY_STORAGE_KEY, JSON.stringify(recentActivities));
  }, [recentActivities]);

  useEffect(() => {
    window.localStorage.setItem(FAVORITE_GROUPS_STORAGE_KEY, JSON.stringify(favoriteGroups));
  }, [favoriteGroups]);

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
  const missingGroupFileCount = Object.values(groupStats).reduce(
    (total, stats) => total + Math.max(stats.total - stats.existing, 0),
    0
  );

  const filesToOpen = useMemo(() => {
    if (checkedFiles.size === 0) {
      return selectedFiles;
    }
    return selectedFiles.filter((file) => checkedFiles.has(normalizeIdentity(file)));
  }, [selectedFiles, checkedFiles]);

  const smartSuggestions = useMemo(
    () => deriveSmartGroupSuggestions(selectedFiles).slice(0, 4),
    [selectedFiles]
  );

  const favoriteGroupEntries = useMemo(
    () => getFavoriteGroupEntries(favoriteGroups, groups),
    [favoriteGroups, groups]
  );

  const visibleFavoriteGroups = useMemo(
    () => pruneFavoriteGroups(favoriteGroups, groups),
    [favoriteGroups, groups]
  );

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

  const rememberRecentActivity = useCallback((kind: 'current' | 'group', title: string, files: string[]) => {
    setRecentActivities((previous) => addRecentActivity(createRecentActivity(kind, title, files), previous));
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

  const handleSelectFiles = useCallback(async () => {
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
  }, [addFilesToSelection, notify]);

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

  const selectSmartSuggestion = (suggestion: SmartGroupSuggestion) => {
    setCheckedFiles(new Set(suggestion.files.map((file) => normalizeIdentity(file))));
    notify(`已勾选“${suggestion.title}”中的 ${suggestion.count} 个文件`, 'success');
  };

  const saveSmartSuggestion = async (suggestion: SmartGroupSuggestion) => {
    try {
      await api.saveGroup(suggestion.title, suggestion.files);
      await refreshGroups();
      notify(`已保存智能文件组“${suggestion.title}”`, 'success');
    } catch (error) {
      console.error(error);
      notify(`保存智能文件组失败: ${String(error)}`, 'danger');
    }
  };

  const handleOpenSelectedFiles = useCallback(async () => {
    if (filesToOpen.length === 0) {
      notify('没有可打开的文件', 'neutral');
      return;
    }

    try {
      const result = await api.openFiles(filesToOpen);
      rememberRecentActivity('current', '当前文件列表', filesToOpen);
      recordOpenResult(result.successCount, result.failedFiles);
    } catch (error) {
      console.error(error);
      notify(`打开文件失败: ${String(error)}`, 'danger');
    }
  }, [filesToOpen, notify, recordOpenResult, rememberRecentActivity]);

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
      rememberRecentActivity('group', name, files);
      recordOpenResult(result.successCount, result.failedFiles);
    } catch (error) {
      console.error(error);
      notify(`打开文件组失败: ${String(error)}`, 'danger');
    }
  };

  const handleLoadGroup = (name: string) => {
    const files = groups[name] ?? [];
    if (files.length === 0) {
      notify('该文件组没有文件', 'neutral');
      return;
    }

    addFilesToSelection(files);
    notify(`已载入文件组“${name}”中的 ${files.length} 个文件`, 'success');
  };

  const handleCopyGroupPaths = async (name: string) => {
    const files = groups[name] ?? [];
    if (files.length === 0) {
      notify('该文件组没有可复制的文件', 'neutral');
      return;
    }

    try {
      await navigator.clipboard.writeText(files.join('\n'));
      notify(`已复制文件组“${name}”的 ${files.length} 个路径`, 'success');
    } catch (error) {
      console.error(error);
      notify(`复制文件组路径失败: ${String(error)}`, 'danger');
    }
  };

  const handleToggleFavoriteGroup = (name: string) => {
    const nextFavorite = !favoriteGroups.includes(name);
    setFavoriteGroups((previous) => toggleFavoriteGroup(previous, name));
    notify(nextFavorite ? `已将“${name}”加入星标 Dock` : `已取消“${name}”星标`, 'success');
  };

  const handleDeleteGroup = async () => {
    if (!deleteTarget) {
      return;
    }

    try {
      await api.deleteGroup(deleteTarget);
      setFavoriteGroups((previous) => previous.filter((name) => name !== deleteTarget));
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

  const copyCurrentFilePaths = useCallback(async () => {
    if (filesToOpen.length === 0) {
      notify('没有可复制的文件路径', 'neutral');
      return;
    }

    try {
      await navigator.clipboard.writeText(filesToOpen.join('\n'));
      notify(`已复制 ${filesToOpen.length} 个文件路径`, 'success');
    } catch (error) {
      console.error(error);
      notify(`复制文件路径失败: ${String(error)}`, 'danger');
    }
  }, [filesToOpen, notify]);

  const clearFileList = () => {
    if (selectedFiles.length === 0) {
      return;
    }

    setSelectedFiles([]);
    setCheckedFiles(new Set());
    notify('已清空当前文件列表', 'success');
  };

  const handleRefreshGroups = async () => {
    try {
      await refreshGroups();
      notify('文件组已刷新', 'success');
    } catch (error) {
      console.error(error);
      notify(`刷新文件组失败: ${String(error)}`, 'danger');
    }
  };

  const handleExportGroups = async () => {
    if (Object.keys(groups).length === 0) {
      notify('暂无可导出的文件组', 'neutral');
      return;
    }

    try {
      const targetPath = await save({
        title: '导出文件组备份',
        defaultPath: 'file_groups_backup.json',
        filters: [{ name: 'JSON', extensions: ['json'] }]
      });
      if (!targetPath) {
        return;
      }

      const result = await api.exportGroupsToPath(targetPath);
      notify(`已导出 ${result.groupCount} 个文件组 / ${result.fileCount} 个文件`, 'success');
    } catch (error) {
      console.error(error);
      notify(`导出文件组失败: ${String(error)}`, 'danger');
    }
  };

  const handleImportGroups = async () => {
    try {
      const sourcePath = await open({
        multiple: false,
        directory: false,
        title: '导入文件组备份',
        filters: [{ name: 'JSON', extensions: ['json'] }]
      });
      if (!sourcePath || Array.isArray(sourcePath)) {
        return;
      }

      const result = await api.importGroupsFromPath(sourcePath);
      await refreshGroups();
      const skippedText = result.skippedGroups > 0 ? `，跳过 ${result.skippedGroups} 个无效分组` : '';
      notify(`已导入 ${result.groupCount} 个文件组 / ${result.fileCount} 个文件${skippedText}`, 'success');
    } catch (error) {
      console.error(error);
      notify(`导入文件组失败: ${String(error)}`, 'danger');
    }
  };

  const handleOpenDataDir = async () => {
    try {
      const path = await api.openDataDir();
      notify(`已打开数据目录: ${path}`, 'success');
    } catch (error) {
      console.error(error);
      notify(`打开数据目录失败: ${String(error)}`, 'danger');
    }
  };

  const refreshHealthReport = useCallback(async () => {
    setHealthLoading(true);
    try {
      const report = await api.getGroupsHealth();
      setHealthReport(report);
      notify(
        report.missingCount > 0
          ? `健康扫描完成，发现 ${report.missingCount} 个缺失路径`
          : '健康扫描完成，未发现缺失路径',
        report.missingCount > 0 ? 'danger' : 'success'
      );
    } catch (error) {
      console.error(error);
      notify(`健康扫描失败: ${String(error)}`, 'danger');
    } finally {
      setHealthLoading(false);
    }
  }, [notify]);

  const openHealthCenter = useCallback(() => {
    setHealthModalOpen(true);
    void refreshHealthReport();
  }, [refreshHealthReport]);

  const copyMissingGroupPaths = async () => {
    const missingFiles = healthReport?.groups.flatMap((group) => group.missingFiles) ?? [];
    if (missingFiles.length === 0) {
      notify('没有缺失路径可复制', 'neutral');
      return;
    }

    try {
      await navigator.clipboard.writeText(missingFiles.join('\n'));
      notify(`已复制 ${missingFiles.length} 个缺失路径`, 'success');
    } catch (error) {
      console.error(error);
      notify(`复制缺失路径失败: ${String(error)}`, 'danger');
    }
  };

  const loadRecentActivity = (activity: RecentActivityItem) => {
    addFilesToSelection(activity.files);
    notify(`已载入最近任务“${activity.title}”`, 'success');
  };

  const openRecentActivity = async (activity: RecentActivityItem) => {
    try {
      const result = await api.openFiles(activity.files);
      rememberRecentActivity(activity.kind, activity.title, activity.files);
      recordOpenResult(result.successCount, result.failedFiles);
    } catch (error) {
      console.error(error);
      notify(`打开最近任务失败: ${String(error)}`, 'danger');
    }
  };

  const copyRecentActivityPaths = async (activity: RecentActivityItem) => {
    try {
      await navigator.clipboard.writeText(activity.files.join('\n'));
      notify(`已复制最近任务“${activity.title}”的路径`, 'success');
    } catch (error) {
      console.error(error);
      notify(`复制最近任务路径失败: ${String(error)}`, 'danger');
    }
  };

  const clearRecentActivities = () => {
    setRecentActivities([]);
    notify('已清空最近任务时间线', 'neutral');
  };

  const commandItems: CommandPaletteItem[] = [
    {
      id: 'select-files',
      title: '选择文件',
      description: '添加文件到当前文件列表',
      keywords: ['add', 'open', 'current'],
      shortcut: 'Ctrl O',
      onRun: () => void handleSelectFiles()
    },
    {
      id: 'save-group',
      title: '保存文件组',
      description: selectedFiles.length > 0 ? '把当前列表保存为一个文件组' : '当前没有可保存的文件',
      keywords: ['group', 'save'],
      shortcut: 'Ctrl S',
      disabled: selectedFiles.length === 0,
      onRun: () => setSaveModalOpen(true)
    },
    {
      id: 'open-current-files',
      title: '打开当前文件',
      description: checkedCount > 0 ? `打开 ${checkedCount} 个已勾选文件` : '未勾选时打开当前列表全部文件',
      keywords: ['launch', 'run', 'open'],
      shortcut: 'Ctrl Enter',
      disabled: selectedFiles.length === 0,
      tone: 'success',
      onRun: () => void handleOpenSelectedFiles()
    },
    {
      id: 'remove-checked-files',
      title: '移除选中文件',
      description: checkedCount > 0 ? `从当前列表移除 ${checkedCount} 个文件` : '请先勾选要移除的文件',
      keywords: ['delete', 'remove', 'clean'],
      disabled: checkedCount === 0,
      tone: 'danger',
      onRun: handleRemoveSelectedFiles
    },
    {
      id: 'copy-current-paths',
      title: '复制当前路径',
      description: '复制已勾选文件路径，未勾选时复制全部路径',
      keywords: ['copy', 'path', 'clipboard'],
      shortcut: 'Ctrl Shift C',
      disabled: filesToOpen.length === 0,
      onRun: () => void copyCurrentFilePaths()
    },
    ...(smartSuggestions.length > 0
      ? [{
          id: 'save-smart-suggestion',
          title: `保存智能建议：${smartSuggestions[0].title}`,
          description: `将 ${smartSuggestions[0].count} 个文件直接保存为文件组`,
          keywords: ['smart', 'suggestion', 'group'],
          tone: 'success' as const,
          onRun: () => void saveSmartSuggestion(smartSuggestions[0])
        }]
      : []),
    {
      id: 'clear-current-list',
      title: '清空当前列表',
      description: '移除当前文件列表里的所有文件',
      keywords: ['clear', 'reset'],
      disabled: selectedFiles.length === 0,
      tone: 'danger',
      onRun: clearFileList
    },
    {
      id: 'expand-groups',
      title: '展开可见文件组',
      description: `展开当前筛选结果中的 ${filteredGroupEntries.length} 个文件组`,
      keywords: ['expand', 'groups'],
      disabled: filteredGroupEntries.length === 0,
      onRun: expandAllVisibleGroups
    },
    {
      id: 'collapse-groups',
      title: '折叠全部文件组',
      description: '收起所有已展开的文件组',
      keywords: ['collapse', 'groups'],
      disabled: expandedGroups.size === 0,
      onRun: collapseAllGroups
    },
    {
      id: 'refresh-groups',
      title: '刷新文件组',
      description: '重新读取文件组和存在性统计',
      keywords: ['reload', 'sync'],
      onRun: () => void handleRefreshGroups()
    },
    {
      id: 'health-center',
      title: '打开健康中心',
      description: missingGroupFileCount > 0
        ? `检查 ${missingGroupFileCount} 个缺失路径`
        : '检查文件组路径可用性',
      keywords: ['health', 'missing', 'scan', 'check'],
      tone: missingGroupFileCount > 0 ? 'danger' : 'success',
      onRun: openHealthCenter
    },
    {
      id: 'recent-activity',
      title: '打开最近任务时间线',
      description: recentActivities.length > 0
        ? `回到 ${recentActivities.length} 条最近任务`
        : '查看最近打开过的文件列表和文件组',
      keywords: ['recent', 'history', 'timeline'],
      disabled: recentActivities.length === 0,
      onRun: () => setRecentModalOpen(true)
    },
    ...(favoriteGroupEntries.length > 0
      ? [{
          id: 'open-first-favorite',
          title: `打开星标文件组：${favoriteGroupEntries[0][0]}`,
          description: `快速打开 Dock 中的 ${favoriteGroupEntries[0][1].length} 个文件`,
          keywords: ['favorite', 'dock', 'star'],
          tone: 'success' as const,
          onRun: () => void handleOpenGroup(favoriteGroupEntries[0][0])
        }]
      : []),
    {
      id: 'import-groups',
      title: '导入文件组',
      description: '从 JSON 备份导入文件组',
      keywords: ['import', 'json', 'backup'],
      onRun: () => void handleImportGroups()
    },
    {
      id: 'export-groups',
      title: '导出文件组',
      description: Object.keys(groups).length > 0 ? '把文件组导出为 JSON 备份' : '暂无可导出的文件组',
      keywords: ['export', 'json', 'backup'],
      disabled: Object.keys(groups).length === 0,
      onRun: () => void handleExportGroups()
    },
    {
      id: 'open-data-dir',
      title: '打开数据目录',
      description: '在资源管理器中打开应用数据目录',
      keywords: ['folder', 'data', 'appdata'],
      onRun: () => void handleOpenDataDir()
    },
    {
      id: 'toggle-theme',
      title: themeMode === 'dark' ? '切换到白天模式' : '切换到黑夜模式',
      description: '播放圆形扩散动效并切换主题',
      keywords: ['theme', 'dark', 'light'],
      disabled: themeAnimating,
      onRun: toggleThemeMode
    },
    {
      id: 'show-shortcuts',
      title: '查看快捷键',
      description: '打开快捷键说明',
      keywords: ['help', 'keyboard'],
      shortcut: 'Ctrl K',
      onRun: () => setShortcutsModalOpen(true)
    },
    ...(failedFiles.length > 0
      ? [{
          id: 'show-failures',
          title: '查看失败文件',
          description: `查看 ${failedFiles.length} 个打开失败的文件`,
          keywords: ['failure', 'error'],
          tone: 'danger' as const,
          onRun: () => setFailuresModalOpen(true)
        }]
      : [])
  ];

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement | null;
      const isTextInput =
        target instanceof HTMLInputElement ||
        target instanceof HTMLTextAreaElement ||
        Boolean(target?.isContentEditable);
      const key = event.key.toLowerCase();
      const control = event.ctrlKey || event.metaKey;

      if (event.key === 'Escape') {
        if (commandPaletteOpen) {
          setCommandPaletteOpen(false);
        } else if (shortcutsModalOpen) {
          setShortcutsModalOpen(false);
        } else if (failuresModalOpen) {
          setFailuresModalOpen(false);
        } else if (healthModalOpen) {
          setHealthModalOpen(false);
        } else if (recentModalOpen) {
          setRecentModalOpen(false);
        } else if (editModal.open) {
          setEditModal(EMPTY_EDIT_MODAL);
        } else if (saveModalOpen) {
          setSaveModalOpen(false);
        } else if (deleteTarget) {
          setDeleteTarget(null);
        }
        return;
      }

      if (control && key === 'k') {
        event.preventDefault();
        setCommandPaletteOpen((previous) => !previous);
        return;
      }

      if (isTextInput || !control) {
        return;
      }

      if (key === 'o') {
        event.preventDefault();
        void handleSelectFiles();
        return;
      }

      if (key === 's') {
        event.preventDefault();
        if (selectedFiles.length > 0) {
          setSaveModalOpen(true);
        } else {
          notify('当前没有可保存的文件', 'neutral');
        }
        return;
      }

      if (event.key === 'Enter') {
        event.preventDefault();
        void handleOpenSelectedFiles();
        return;
      }

      if (event.shiftKey && key === 'c') {
        event.preventDefault();
        void copyCurrentFilePaths();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [
    commandPaletteOpen,
    copyCurrentFilePaths,
    deleteTarget,
    editModal.open,
    failuresModalOpen,
    healthModalOpen,
    recentModalOpen,
    handleOpenSelectedFiles,
    handleSelectFiles,
    openHealthCenter,
    notify,
    saveModalOpen,
    shortcutsModalOpen,
    selectedFiles.length
  ]);

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
      <WindowTitleBar />
      <div className="app-content">
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
          <button
            className="mini-btn command-trigger"
            type="button"
            onClick={() => setCommandPaletteOpen(true)}
            title="打开指令中心"
          >
            指令中心 <kbd>Ctrl K</kbd>
          </button>
          {failedFiles.length > 0 && (
            <button className="mini-btn status-action" onClick={() => setFailuresModalOpen(true)}>
              查看失败文件
            </button>
          )}
        </div>
      </header>

      <FavoriteGroupsDock
        entries={favoriteGroupEntries}
        onOpenGroup={handleOpenGroup}
        onLoadGroup={handleLoadGroup}
      />

      <main className="app-main">
        <CurrentFilePanel
          selectedFiles={selectedFiles}
          checkedFiles={checkedFiles}
          checkedCount={checkedCount}
          filteredFiles={filteredFiles}
          fileKeyword={fileKeyword}
          dragActive={dragActive}
          smartSuggestions={smartSuggestions}
          onFileKeywordChange={setFileKeyword}
          onSelectFiles={handleSelectFiles}
          onSaveGroupClick={() => setSaveModalOpen(true)}
          onSelectAllFilteredFiles={selectAllFilteredFiles}
          onInvertFilteredSelection={invertFilteredSelection}
          onClearSelection={clearSelection}
          onCopySelectedPaths={copyCurrentFilePaths}
          onClearFileList={clearFileList}
          onToggleFileChecked={handleToggleFileChecked}
          onRemoveSelectedFiles={handleRemoveSelectedFiles}
          onOpenSelectedFiles={handleOpenSelectedFiles}
          onSelectSmartSuggestion={selectSmartSuggestion}
          onSaveSmartSuggestion={saveSmartSuggestion}
        />

        <GroupPanel
          groups={groups}
          groupStats={groupStats}
          filteredGroupEntries={filteredGroupEntries}
          expandedGroups={expandedGroups}
          favoriteGroups={visibleFavoriteGroups}
          groupKeyword={groupKeyword}
          onGroupKeywordChange={setGroupKeyword}
          onExpandAllVisibleGroups={expandAllVisibleGroups}
          onCollapseAllGroups={collapseAllGroups}
          onRefreshGroups={handleRefreshGroups}
          onExportGroups={handleExportGroups}
          onImportGroups={handleImportGroups}
          onOpenDataDir={handleOpenDataDir}
          onToggleGroup={handleToggleGroup}
          onOpenGroup={handleOpenGroup}
          onLoadGroup={handleLoadGroup}
          onCopyGroup={handleCopyGroupPaths}
          onToggleFavoriteGroup={handleToggleFavoriteGroup}
          onEditGroup={openEditModal}
          onDeleteGroup={setDeleteTarget}
        />
      </main>
      </div>

      {commandPaletteOpen && (
        <CommandPalette items={commandItems} onClose={() => setCommandPaletteOpen(false)} />
      )}

      {healthModalOpen && (
        <HealthCenterModal
          report={healthReport}
          loading={healthLoading}
          onRefresh={() => void refreshHealthReport()}
          onCopyMissing={copyMissingGroupPaths}
          onClose={() => setHealthModalOpen(false)}
        />
      )}

      {recentModalOpen && (
        <RecentActivityModal
          items={recentActivities}
          onLoad={loadRecentActivity}
          onOpen={(activity) => void openRecentActivity(activity)}
          onCopy={(activity) => void copyRecentActivityPaths(activity)}
          onClear={clearRecentActivities}
          onClose={() => setRecentModalOpen(false)}
        />
      )}

      {saveModalOpen && (
        <SaveGroupModal
          groupName={saveGroupName}
          onGroupNameChange={setSaveGroupName}
          onCancel={() => setSaveModalOpen(false)}
          onSave={handleSaveGroup}
        />
      )}

      {deleteTarget && (
        <div className="modal-backdrop" style={modalBackdropStyle}>
          <div className="modal" style={modalSurfaceStyle}>
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

      {shortcutsModalOpen && (
        <ShortcutsModal onClose={() => setShortcutsModalOpen(false)} />
      )}
    </div>
  );
}

export default App;
