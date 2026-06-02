export type GroupsRecord = Record<string, string[]>;

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
