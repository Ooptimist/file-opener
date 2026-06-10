export type GroupsRecord = Record<string, string[]>;

export type StatusTone = 'neutral' | 'success' | 'danger';

export type ThemeMode = 'dark' | 'light';

export type StatusState = {
  message: string;
  tone: StatusTone;
};

export type EditModalState = {
  open: boolean;
  originalName: string;
  name: string;
  files: string[];
  checked: Set<string>;
};

export type GroupStats = {
  existing: number;
  total: number;
};

export type OpenFilesResult = {
  successCount: number;
  failedFiles: string[];
};

export type MigrationResult = {
  migrated: boolean;
  source?: string;
};
