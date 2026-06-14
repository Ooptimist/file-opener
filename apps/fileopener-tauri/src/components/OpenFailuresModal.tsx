import { getFileIcon, getFileName } from '../file-utils';
import { modalBackdropStyle, modalSurfaceStyle } from './modalStyles';

type OpenFailuresModalProps = {
  failedFiles: string[];
  onCopy: () => void;
  onClose: () => void;
};

export function OpenFailuresModal({ failedFiles, onCopy, onClose }: OpenFailuresModalProps) {
  return (
    <div className="modal-backdrop" style={modalBackdropStyle}>
      <div className="modal modal-large" style={modalSurfaceStyle}>
        <h3>打开失败的文件</h3>
        <p>以下文件不存在、权限不足，或被系统阻止打开。</p>

        <div className="failure-list">
          {failedFiles.map((file) => (
            <div className="failure-item" key={file} title={file}>
              <span>{getFileIcon(file)} {getFileName(file)}</span>
              <small>{file}</small>
            </div>
          ))}
        </div>

        <div className="modal-actions">
          <button className="btn btn-secondary" onClick={onClose}>关闭</button>
          <button className="btn btn-primary" onClick={onCopy}>复制路径</button>
        </div>
      </div>
    </div>
  );
}
