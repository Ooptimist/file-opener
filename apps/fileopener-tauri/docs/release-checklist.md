# Tauri 发布检查清单（Windows）

## 工具链

- 安装 Rust（含 cargo）
- 安装 Visual Studio C++ Build Tools（MSVC）
- `npm install`
- `npm run build`
- `npm run tauri:build`

## 功能验收

- 主窗口按钮图标显示正常
- 文件列表空状态文案正常
- 支持文件选择和拖拽导入
- 支持勾选后移除
- 支持批量打开（有失败反馈）
- 文件组保存/编辑/删除/展开折叠
- 迁移旧版 `file_groups.json` 成功

## 回归验收

- 新安装无历史数据可正常使用
- 升级安装可读取旧数据
- 路径包含空格/中文可用

## 签名与发布占位

- 代码签名证书配置（待接入）
- CI 构建与产物归档（待接入）
- 版本号策略（待接入）
- 升级说明（待接入）
