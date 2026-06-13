import { normalizeIdentity } from './file-utils.js';

export type RecentActivityKind = 'current' | 'group';

export type RecentActivityItem = {
  id: string;
  kind: RecentActivityKind;
  title: string;
  description: string;
  files: string[];
  createdAt: string;
};

function getActivityFingerprint(kind: RecentActivityKind, files: string[]) {
  return `${kind}:${files.map((file) => normalizeIdentity(file)).sort().join('|')}`;
}

export function createRecentActivity(
  kind: RecentActivityKind,
  title: string,
  files: string[],
  createdAt = new Date().toISOString()
): RecentActivityItem | null {
  const normalizedFiles = files.filter((file) => normalizeIdentity(file));
  if (normalizedFiles.length === 0) {
    return null;
  }

  return {
    id: getActivityFingerprint(kind, normalizedFiles),
    kind,
    title,
    description: `${normalizedFiles.length} 个文件`,
    files: normalizedFiles,
    createdAt
  };
}

export function addRecentActivity(
  activity: RecentActivityItem | null,
  history: RecentActivityItem[],
  limit = 8
) {
  if (!activity) {
    return history;
  }

  return [
    activity,
    ...history.filter((item) => item.id !== activity.id)
  ].slice(0, limit);
}
