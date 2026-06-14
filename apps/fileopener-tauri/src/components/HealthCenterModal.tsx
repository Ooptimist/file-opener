import type { GroupHealthReport } from '../types';
import { modalBackdropStyle, modalSurfaceStyle } from './modalStyles';

type HealthCenterModalProps = {
  report: GroupHealthReport | null;
  loading: boolean;
  onRefresh: () => void;
  onCopyMissing: () => void;
  onClose: () => void;
};

function getHealthScore(report: GroupHealthReport | null) {
  if (!report || report.fileCount === 0) {
    return 100;
  }
  return Math.round((report.existingCount / report.fileCount) * 100);
}

export function HealthCenterModal({
  report,
  loading,
  onRefresh,
  onCopyMissing,
  onClose
}: HealthCenterModalProps) {
  const score = getHealthScore(report);
  const problemGroups = report?.groups.filter((group) => group.missingFiles.length > 0) ?? [];
  const missingCount = report?.missingCount ?? 0;

  return (
    <div className="modal-backdrop" style={modalBackdropStyle}>
      <div className="modal modal-large health-modal" style={modalSurfaceStyle}>
        <div className="health-hero">
          <div>
            <span className="command-kicker">Health Center</span>
            <h3>文件组健康中心</h3>
            <p>检查文件组路径是否仍然可用，提前发现移动、删除或权限变化导致的问题。</p>
          </div>
          <div className={`health-score ${missingCount > 0 ? 'is-warning' : 'is-good'}`}>
            <strong>{score}</strong>
            <span>健康分</span>
          </div>
        </div>

        <div className="health-metrics">
          <div>
            <span>文件组</span>
            <strong>{report?.groupCount ?? 0}</strong>
          </div>
          <div>
            <span>总文件</span>
            <strong>{report?.fileCount ?? 0}</strong>
          </div>
          <div>
            <span>可用</span>
            <strong>{report?.existingCount ?? 0}</strong>
          </div>
          <div className={missingCount > 0 ? 'danger' : ''}>
            <span>缺失</span>
            <strong>{missingCount}</strong>
          </div>
        </div>

        <div className="health-list">
          {loading ? (
            <div className="health-empty">正在扫描文件组...</div>
          ) : problemGroups.length === 0 ? (
            <div className="health-empty">所有文件组路径都可用，状态很干净。</div>
          ) : (
            problemGroups.map((group) => (
              <section className="health-group" key={group.name}>
                <div className="health-group-head">
                  <strong>{group.name}</strong>
                  <span>{group.existing} / {group.total} 可用</span>
                </div>
                <div className="health-missing-list">
                  {group.missingFiles.map((file) => (
                    <code key={file} title={file}>{file}</code>
                  ))}
                </div>
              </section>
            ))
          )}
        </div>

        <div className="modal-actions">
          <button className="btn btn-secondary" onClick={onRefresh} disabled={loading}>重新扫描</button>
          <button className="btn btn-secondary" onClick={onCopyMissing} disabled={loading || missingCount === 0}>
            复制缺失路径
          </button>
          <button className="btn btn-primary" onClick={onClose}>关闭</button>
        </div>
      </div>
    </div>
  );
}
