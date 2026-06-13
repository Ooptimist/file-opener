import { getFileName, normalizeIdentity } from './file-utils.js';

export type SmartGroupSuggestion = {
  id: string;
  title: string;
  description: string;
  count: number;
  files: string[];
  accent: 'blue' | 'green' | 'orange' | 'red' | 'gray';
};

const CATEGORY_DEFINITIONS = [
  {
    id: 'documents',
    title: '文档资料',
    description: 'PDF、Markdown、Word、文本等资料文件',
    accent: 'blue' as const,
    extensions: new Set(['pdf', 'doc', 'docx', 'txt', 'md', 'rtf'])
  },
  {
    id: 'images',
    title: '图片素材',
    description: '常见图片、截图和视觉素材',
    accent: 'orange' as const,
    extensions: new Set(['png', 'jpg', 'jpeg', 'webp', 'gif', 'svg', 'bmp'])
  },
  {
    id: 'spreadsheets',
    title: '表格数据',
    description: 'Excel、CSV、TSV 等数据表',
    accent: 'green' as const,
    extensions: new Set(['xls', 'xlsx', 'csv', 'tsv'])
  },
  {
    id: 'code',
    title: '代码文件',
    description: '脚本、配置和源码文件',
    accent: 'gray' as const,
    extensions: new Set(['ts', 'tsx', 'js', 'jsx', 'py', 'rs', 'json', 'css', 'html', 'yaml', 'yml', 'toml'])
  },
  {
    id: 'installers',
    title: '安装与压缩包',
    description: '安装程序、快捷方式和归档文件',
    accent: 'red' as const,
    extensions: new Set(['exe', 'msi', 'zip', 'rar', '7z', 'lnk'])
  }
];

function getExtension(file: string) {
  const fileName = getFileName(file);
  const dotIndex = fileName.lastIndexOf('.');
  if (dotIndex < 0 || dotIndex === fileName.length - 1) {
    return '';
  }
  return fileName.slice(dotIndex + 1).toLowerCase();
}

function dedupeFiles(files: string[]) {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const file of files) {
    const key = normalizeIdentity(file);
    if (!key || seen.has(key)) {
      continue;
    }
    seen.add(key);
    out.push(file);
  }
  return out;
}

export function deriveSmartGroupSuggestions(files: string[]): SmartGroupSuggestion[] {
  const uniqueFiles = dedupeFiles(files);
  if (uniqueFiles.length < 2) {
    return [];
  }

  return CATEGORY_DEFINITIONS
    .map((category) => {
      const matchedFiles = uniqueFiles.filter((file) => category.extensions.has(getExtension(file)));
      return {
        id: category.id,
        title: category.title,
        description: category.description,
        count: matchedFiles.length,
        files: matchedFiles,
        accent: category.accent
      };
    })
    .filter((suggestion) => suggestion.count >= 2);
}
