type FavoriteGroupsDockProps = {
  entries: [string, string[]][];
  onOpenGroup: (name: string) => void;
  onLoadGroup: (name: string) => void;
};

export function FavoriteGroupsDock({ entries, onOpenGroup, onLoadGroup }: FavoriteGroupsDockProps) {
  if (entries.length === 0) {
    return null;
  }

  return (
    <section className="favorite-dock" aria-label="星标文件组 Dock">
      <div className="favorite-dock-title">
        <span>星标 Dock</span>
        <small>{entries.length} 个常用文件组</small>
      </div>
      <div className="favorite-dock-list">
        {entries.map(([name, files]) => (
          <article className="favorite-dock-item" key={name}>
            <div className="favorite-dock-icon" aria-hidden="true">★</div>
            <div className="favorite-dock-main">
              <strong title={name}>{name}</strong>
              <span>{files.length} 个文件</span>
            </div>
            <div className="favorite-dock-actions">
              <button className="mini-btn" type="button" onClick={() => onLoadGroup(name)}>载入</button>
              <button className="mini-btn" type="button" onClick={() => onOpenGroup(name)}>打开</button>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
