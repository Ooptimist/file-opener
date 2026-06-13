import type { GroupsRecord } from './types.js';

export function toggleFavoriteGroup(favorites: string[], name: string) {
  if (favorites.includes(name)) {
    return favorites.filter((favorite) => favorite !== name);
  }
  return [...favorites, name];
}

export function pruneFavoriteGroups(favorites: string[], groups: GroupsRecord) {
  return favorites.filter((name) => Object.prototype.hasOwnProperty.call(groups, name));
}

export function getFavoriteGroupEntries(favorites: string[], groups: GroupsRecord): [string, string[]][] {
  return pruneFavoriteGroups(favorites, groups).map((name) => [name, groups[name]]);
}
