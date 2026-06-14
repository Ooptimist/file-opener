# AGENT 规约

本文档用于约束在本项目中执行开发任务时的默认行为与质量标准。

## 1. 目标与原则

- 优先保证功能正确，其次优化体验和美观。
- 小步修改，避免一次性大改动导致回归风险。
- 不改业务语义，仅在需求明确时调整逻辑。
- 所有改动应可追踪、可解释、可回滚。

## 2. 代码与结构规范

- 遵循现有项目结构，不随意新增层级。
- 复用已有模块：`src/defines.py`、`src/utils.py`、`src/ui/*`。
- 常量统一放在 `src/defines.py`，禁止在业务代码中硬编码颜色、尺寸、文案。
- 优先复用工具函数，避免重复实现。
- 新增代码默认使用 ASCII，除非中文文案确有必要。

## 3. UI 规范（深色专业风）

- 统一使用设计 token（颜色、圆角、间距、字体）。
- 按钮优先采用 `图标 + 文字`，保证可读性。
- 图标资源使用本地文件，不依赖运行时网络请求。
- 文件列表、分组卡片、弹窗样式保持同一视觉语言。
- 空状态必须有提示文案（例如无文件、无文件组）。
- Tauri/WebView2 中涉及高斯模糊的浮层（菜单、指令中心、弹窗等）不能只依赖 CSS 的 `backdrop-filter`；必须同时在 React 节点上设置 `backdropFilter` 和 `WebkitBackdropFilter` 的 inline style，避免 Vite 生产构建优化后 release 版模糊失效。普通弹窗统一复用 `apps/fileopener-tauri/src/components/modalStyles.ts`。

## 4. 图标与资源规范

- 图标目录：`src/assets/icons/fluent/`。
- 运行时允许从以下路径兜底加载：
  - `assets/icons/fluent/`
  - `src/assets/icons/fluent/`
- 资源许可信息写入：`src/assets/icons/ATTRIBUTION.md`。
- 打包时必须包含资源目录（见 `FileOpener.spec` 的 `datas` 配置）。

## 5. 质量与验证

- 每次改动后至少执行语法检查：
  - `python -m py_compile main.py src/defines.py src/utils.py src/ui/ui_components.py src/ui/dialogs.py`
- 涉及 UI 变更时，手动验证：
  - 主窗口按钮图标显示
  - 文件列表空状态
  - 文件组展开/折叠
  - 编辑文件组弹窗按钮图标
- 涉及 Tauri 高斯模糊或浮层样式变更时，必须执行 `npm run tauri:build`，并打开 `apps/fileopener-tauri/src-tauri/target/release/fileopener_tauri.exe` 手动检查；只跑 dev 或 `npm run build` 不能证明 release 版生效。

## 6. Git 与提交规范

- 不主动提交，除非明确要求。
- 不使用破坏性命令（`reset --hard`、强制覆盖等）。
- 提交信息聚焦变更目的与收益，避免只描述文件名。
- 禁止提交敏感信息（账号、密钥、路径隐私等）。
- 提交时备注内容使用中文。

## 7. 沟通规范

- 先执行再汇报，除非存在阻塞风险。
- 汇报内容包含：改了什么、为什么、改动文件、如何验证。
- 若有兼容性或取舍，明确说明默认方案和后续可选项。

## 8. 固定流程

- 每次做完改动后，使用pyinstaller打包出最新的exe文件。

---

如与用户最新明确指令冲突，以用户指令为准。
