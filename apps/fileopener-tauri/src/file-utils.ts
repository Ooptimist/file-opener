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

export function getFileName(path: string) {
  const normalized = path.replace(/\//g, '\\');
  const idx = normalized.lastIndexOf('\\');
  return idx >= 0 ? normalized.slice(idx + 1) : normalized;
}

export function getFileIcon(path: string) {
  const name = getFileName(path);
  const idx = name.lastIndexOf('.');
  if (idx < 0) {
    return DEFAULT_FILE_ICON;
  }
  const ext = name.slice(idx).toLowerCase();
  return FILE_ICONS[ext] ?? DEFAULT_FILE_ICON;
}

export function normalizeIdentity(path: string) {
  return path.trim().replace(/\//g, '\\').toLowerCase();
}

export function mergeAndDedupeFiles(current: string[], incoming: string[]) {
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
