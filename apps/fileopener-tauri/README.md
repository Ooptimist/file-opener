# FileOpener Tauri (并行重写版)

该目录是 FileOpener 的 Tauri v2 并行重写工程，目标是先实现与 Python 版本的 1:1 功能等价，再迭代体验。

## 当前已实现

- React + TypeScript + Vite 前端骨架
- Tauri v2 后端 commands（Rust）
  - `load_groups`
  - `save_group`
  - `rename_group`
  - `delete_group`
  - `update_group_files`
  - `get_group_stats`
  - `open_files`
  - `migrate_legacy_groups`
- AppData 下 `file_groups.json` 持久化
- 启动时一次性旧数据迁移
- 文件选择、拖拽导入、批量移除、批量打开
- 文件组展开/折叠、打开、编辑、删除
- 深色专业风 UI 与本地图标资源

## 本地运行

```bash
cd apps/fileopener-tauri
npm install
npm run dev
```

## Tauri 运行

```bash
npm run tauri:dev
npm run tauri:build
```

Windows 推荐直接执行：

```bash
dev-tauri.bat
build-tauri.bat
```

这两个脚本会自动加载 VS Build Tools 编译环境并补充 cargo 到 PATH。

## 目录说明

- `src/` 前端页面与样式
- `src/tauri-api.ts` 前端调用 Rust commands
- `src-tauri/src/services/group_service.rs` 分组与持久化
- `src-tauri/src/services/file_open_service.rs` 文件打开能力
- `src-tauri/src/services/migration_service.rs` 旧数据迁移
- `src-tauri/src/lib.rs` command 注册与应用入口
- `.cargo/config.toml` Cargo 镜像配置（USTC sparse）

## 发布与验收

请参考 `docs/release-checklist.md`。
