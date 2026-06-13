export type CommandPaletteSearchItem = {
  title: string;
  description: string;
  keywords?: string[];
};

export function filterCommandItems<T extends CommandPaletteSearchItem>(items: T[], query: string): T[] {
  const normalizedQuery = query.trim().toLowerCase();
  if (!normalizedQuery) {
    return items;
  }

  return items.filter((item) => {
    const searchableText = [
      item.title,
      item.description,
      ...(item.keywords ?? [])
    ].join(' ').toLowerCase();
    return searchableText.includes(normalizedQuery);
  });
}
