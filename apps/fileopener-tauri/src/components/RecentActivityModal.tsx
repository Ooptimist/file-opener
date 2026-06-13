import type { RecentActivityItem } from '../recent-activity-utils';

type RecentActivityModalProps = {
  items: RecentActivityItem[];
  onLoad: (item: RecentActivityItem) => void;
  onOpen: (item: RecentActivityItem) => void;
  onCopy: (item: RecentActivityItem) => void;
  onClear: () => void;
  onClose: () => void;
};

function formatActivityTime(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return '刚刚';
  }
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
}

export function RecentActivityModal({
  items,
  onLoad,
  onOpen,
  onCopy,
  onClear,
  onClose
}: RecentActivityModalProps) {
  return (
    <div className="modal-backdrop">
      <div className="modal modal-large recent-modal">
        <div className="recent-hero">
          <div>
            <span className="command-kicker">Timeline</span>
            <h3>最近任务时间线</h3>
            <p>回到刚才打开过的上下文，重新载入、再次打开或复制路径。</p>
          </div>
          <div className="recent-count">
            <strong>{items.length}</strong>
            <span>条记录</span>
          </div>
        </div>

        <div className="recent-list">
          {items.length === 0 ? (
            <div className="recent-empty">还没有最近任务。打开当前列表或文件组后，这里会自动记录。</div>
          ) : (
            items.map((item) => (
              <article className="recent-item" key={item.id}>
                <div className="recent-marker" aria-hidden="true" />
                <div className="recent-main">
                  <div className="recent-title-row">
                    <strong>{item.title}</strong>
                    <time>{formatActivityTime(item.createdAt)}</time>
                  </div>
                  <span>{item.kind === 'group' ? '文件组任务' : '当前列表任务'} · {item.description}</span>
                </div>
                <div className="recent-actions">
                  <button className="mini-btn" onClick={() => onLoad(item)}>载入</button>
                  <button className="mini-btn" onClick={() => onOpen(item)}>打开</button>
                  <button className="mini-btn" onClick={() => onCopy(item)}>复制</button>
                </div>
              </article>
            ))
          )}
        </div>

        <div className="modal-actions">
          <button className="btn btn-secondary" onClick={onClear} disabled={items.length === 0}>清空记录</button>
          <button className="btn btn-primary" onClick={onClose}>关闭</button>
        </div>
      </div>
    </div>
  );
}
