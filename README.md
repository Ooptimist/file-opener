# 文件批量打开工具（FileOpener）

一个面向 Windows 的桌面工具，用于集中管理常用文件并进行批量打开。

## 功能概览

### 1. 当前文件列表
- 支持通过「选择文件」一次性添加多个文件。
- 支持将文件直接拖拽到当前文件列表区域。
- 列表项整行可点击勾选（不只文件名区域）。
- 鼠标悬停文件项时显示完整路径。
- 支持批量移除已勾选文件。
- 支持批量打开文件：
  - 勾选了文件时，仅打开勾选项。
  - 未勾选时，默认打开当前列表全部文件。
- 自动按扩展名显示文件图标（未知类型显示默认图标）。

### 2. 文件组管理
- 可将当前文件列表保存为文件组。
- 文件组数据自动持久化，重启后仍保留。
- 每个文件组显示「存在文件数 / 总文件数」。
- 文件组支持展开/折叠查看明细。
- 展开后可查看组内每个文件状态（存在/丢失标记）。
- 展开项支持悬停显示完整路径（文件名保持原色，路径为弱化色）。
- 每个文件组支持：打开、编辑、删除。

### 3. 编辑/确认弹窗
- 包含保存分组、删除确认、编辑分组三个弹窗。
- 弹窗相对主窗口居中显示。
- 弹窗采用平滑显现流程，减少首开闪烁与突兀感。
- 编辑弹窗支持：添加文件、勾选删除、保存。
- 系统文件选择框会绑定当前窗口/弹窗作为 parent，位置更稳定。

### 4. 图标与视觉
- 主窗口与弹窗均使用项目图标（非 Python 默认图标）。
- 按钮使用本地图标资源（`src/assets/icons/fluent/`）。
- 界面采用统一深色风格设计 token（颜色、圆角、间距、字体）。

## 技术栈
- Python 3.11+
- CustomTkinter
- tkinterdnd2
- Pillow
- PyInstaller（打包时）

## 快速开始（开发环境）

### 1. 安装依赖
```bash
pip install customtkinter tkinterdnd2 pillow pyinstaller
```

### 2. 运行程序
```bash
python main.py
```

## 打包 EXE

### 推荐方式
```bash
build.bat
```

### 手动方式
```bash
python -m PyInstaller --clean --noconfirm FileOpener.spec
```

输出文件：`dist/FileOpener.exe`

## 数据与资源说明
- 文件组数据：`file_groups.json`
  - 开发模式：位于 `src/file_groups.json`
  - 打包运行：位于 EXE 同目录
- 程序图标：`icon.ico`
- 按钮图标资源：`src/assets/icons/fluent/`
- 图标许可说明：`src/assets/icons/ATTRIBUTION.md`

## 项目结构（核心）

```text
autoopen/
├─ main.py
├─ build.bat
├─ FileOpener.spec
├─ icon.ico
├─ README.md
└─ src/
   ├─ defines.py
   ├─ utils.py
   ├─ file_groups.json
   ├─ assets/
   │  └─ icons/
   │     ├─ ATTRIBUTION.md
   │     └─ fluent/
   ├─ handlers/
   │  ├─ file_handler.py
   │  ├─ group_manager.py
   │  ├─ tkdnd_drop_zone.py
   │  └─ drag_drop.py
   └─ ui/
      ├─ dialogs.py
      └─ ui_components.py
```

## 常见问题

### 1. 运行 EXE 报错 `ModuleNotFoundError: No module named 'tkinter'`
当前 Python 环境缺少 Tcl/Tk 组件。请重装 Python 并确保安装 Tcl/Tk（Windows 安装器默认可勾选）。

### 2. 打包时报 EXE 被占用
请先关闭正在运行的 `FileOpener.exe`，再执行 `build.bat`。

### 3. 打开文件出现 UAC 提示
若用户在 UAC 中选择“否”，程序会将该文件记为失败项，不会重复弹同一文件的二次提示。

## 适用平台
- Windows 10 / 11
