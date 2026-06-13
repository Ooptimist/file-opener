import { invoke } from '@tauri-apps/api/core';
import type {
  ExportGroupsResult,
  GroupHealthReport,
  GroupStats,
  GroupsRecord,
  ImportGroupsResult,
  MigrationResult,
  OpenFilesResult
} from './types';

export const api = {
  loadGroups: () => invoke<GroupsRecord>('load_groups'),
  saveGroup: (name: string, files: string[]) => invoke<void>('save_group', { name, files }),
  renameGroup: (oldName: string, newName: string) =>
    invoke<void>('rename_group', { oldName, newName }),
  deleteGroup: (name: string) => invoke<void>('delete_group', { name }),
  updateGroupFiles: (name: string, files: string[]) =>
    invoke<void>('update_group_files', { name, files }),
  getGroupStats: (name: string) => invoke<GroupStats>('get_group_stats', { name }),
  getGroupsHealth: () => invoke<GroupHealthReport>('get_groups_health'),
  openFiles: (files: string[]) => invoke<OpenFilesResult>('open_files', { files }),
  migrateLegacyGroups: () => invoke<MigrationResult>('migrate_legacy_groups'),
  getGroupsFilePath: () => invoke<string>('get_groups_file_path'),
  exportGroupsToPath: (path: string) => invoke<ExportGroupsResult>('export_groups_to_path', { path }),
  importGroupsFromPath: (path: string) => invoke<ImportGroupsResult>('import_groups_from_path', { path }),
  openDataDir: () => invoke<string>('open_data_dir')
};
