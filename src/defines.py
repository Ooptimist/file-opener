"""
defines.py
全局配置和常量定义文件

此文件集中管理所有可调整的常量，方便修改和调试
修改后重启程序生效
"""

import os
import sys

# ========================================
# 窗口设置
# ========================================
WINDOW_TITLE = "文件批量打开工具"           # 窗口标题
WINDOW_WIDTH = 1600                         # 窗口默认宽度
WINDOW_HEIGHT = 1000                        # 窗口默认高度
WINDOW_MIN_WIDTH = 1000                     # 窗口最小宽度
WINDOW_MIN_HEIGHT = 700                     # 窗口最小高度
WINDOW_RESIZABLE = True                     # 是否允许调整窗口大小

# ========================================
# 主题设置
# ========================================
THEME_APPEARANCE = "dark"                   # 外观模式: "dark" 或 "light"
THEME_COLOR = "blue"                        # 主题颜色: "blue", "green", "dark-blue"

# ========================================
# 字体设置（Microsoft YaHei 确保中文显示正常）
# ========================================
FONT_FAMILY = "Microsoft YaHei"             # 字体族名

# 通用字体
FONT_SIZE_TITLE = 22                        # 标题字体大小
FONT_SIZE_HEADER = 16                       # 副标题字体大小
FONT_SIZE_NORMAL = 13                       # 正文字体大小
FONT_SIZE_SMALL = 12                        # 小字体大小
FONT_SIZE_TINY = 10                         # 极小字体大小

# 对话框字体
FONT_SIZE_DIALOG = 14                       # 对话框正文字体大小
FONT_SIZE_DIALOG_TITLE = 16                 # 对话框标题字体大小

# 文件组专用字体
FONT_SIZE_GROUP_TITLE = 18                  # 文件组标题字体大小
FONT_SIZE_GROUP_NAME = 14                   # 文件组名称字体大小
FONT_SIZE_GROUP_COUNT = 12                  # 文件组计数字体大小
FONT_SIZE_GROUP_FILE = 11                   # 文件列表字体大小

# 图标字体
FONT_SIZE_ICON = 14                         # 图标字体大小

# ========================================
# 颜色设置
# ========================================
# 按钮颜色
COLOR_PRIMARY = "#3498db"                   # 主按钮颜色（蓝色）
COLOR_PRIMARY_HOVER = "#2980b9"             # 主按钮悬停颜色

COLOR_SUCCESS = "#27ae60"                   # 成功/打开按钮颜色（绿色）
COLOR_SUCCESS_HOVER = "#1e8449"             # 成功按钮悬停颜色

COLOR_DANGER = "#e74c3c"                    # 危险/删除按钮颜色（红色）
COLOR_DANGER_HOVER = "#c0392b"              # 危险按钮悬停颜色

COLOR_SECONDARY = "#34495e"                 # 次要按钮颜色（深灰）
COLOR_SECONDARY_HOVER = "#2c3e50"           # 次要按钮悬停颜色

# 背景颜色
COLOR_BG_FRAME = "#2b2b2b"                  # 框架背景颜色
COLOR_BG_FILE_LIST = "#1e1e1e"              # 文件列表背景颜色

# 文字颜色
COLOR_TEXT_GRAY = "gray"                    # 灰色文字

# ========================================
# UI 尺寸设置
# ========================================
# 按钮高度
BUTTON_HEIGHT_LARGE = 40                    # 大按钮高度
BUTTON_HEIGHT_NORMAL = 38                   # 普通按钮高度
BUTTON_HEIGHT_SMALL = 32                    # 小按钮高度
BUTTON_HEIGHT_ICON = 30                     # 图标按钮高度

# 按钮宽度
BUTTON_WIDTH_ICON = 60                      # 图标按钮宽度
BUTTON_WIDTH_SMALL = 80                     # 小按钮宽度

# 圆角半径
CORNER_RADIUS_LARGE = 10                    # 大圆角（窗口框架）
CORNER_RADIUS_NORMAL = 8                    # 普通圆角
CORNER_RADIUS_SMALL = 6                     # 小圆角（按钮）
CORNER_RADIUS_TINY = 4                      # 极小圆角

# 间距
PAD_X_LARGE = 20                            # 大水平间距
PAD_X_NORMAL = 15                           # 普通水平间距
PAD_X_SMALL = 10                            # 小水平间距
PAD_X_TINY = 6                              # 极小水平间距

PAD_Y_LARGE = 25                            # 大垂直间距
PAD_Y_NORMAL = 15                           # 普通垂直间距
PAD_Y_SMALL = 10                            # 小垂直间距
PAD_Y_TINY = 8                              # 极小垂直间距

# 边距
MARGIN_FRAME = 8                            # 框架内边距

# ========================================
# 文件组设置
# ========================================
GROUPS_FILE_NAME = "file_groups.json"       # 文件组保存文件名

# ========================================
# 对话框设置
# ========================================
DIALOG_SAVE_WIDTH = 380                     # 保存对话框宽度
DIALOG_SAVE_HEIGHT = 200                    # 保存对话框高度
DIALOG_DELETE_WIDTH = 320                   # 删除对话框宽度
DIALOG_DELETE_HEIGHT = 130                  # 删除对话框高度
DIALOG_EDIT_WIDTH = 600                     # 编辑对话框宽度
DIALOG_EDIT_HEIGHT = 500                    # 编辑对话框高度

# ========================================
# 文件选择器设置
# ========================================
FILE_DIALOG_TITLE = "选择文件"              # 文件选择对话框标题
FILE_TYPES = [                              # 文件类型过滤器
    ("所有文件", "*.*"),
    ("文本文件", "*.txt"),
    ("图片文件", "*.png *.jpg *.jpeg *.gif"),
    ("文档文件", "*.pdf *.doc *.docx")
]

# ========================================
# 文件图标映射
# ========================================
FILE_ICONS = {
    # 文本文件
    ".txt": "📝",
    # 文档文件
    ".pdf": "📕",
    ".doc": "📘",
    ".docx": "📘",
    # 表格文件
    ".xls": "📊",
    ".xlsx": "📊",
    # 演示文件
    ".ppt": "📙",
    ".pptx": "📙",
    # 图片文件
    ".png": "🖼️",
    ".jpg": "🖼️",
    ".jpeg": "🖼️",
    ".gif": "🖼️",
    # 音频视频
    ".mp3": "🎵",
    ".mp4": "🎬",
    # 压缩文件
    ".zip": "📦",
    ".rar": "📦",
    # 可执行文件
    ".exe": "⚙️",
    # 代码文件
    ".py": "🐍",
    ".js": "📜",
    ".html": "🌐",
    ".css": "🎨",
}
DEFAULT_FILE_ICON = "📄"                    # 默认文件图标

# ========================================
# 图标资源
# ========================================
ICON_FILE_NAME = "icon.ico"                 # 图标文件名
APP_ID = "FileOpenerApp.FileOpener.1.0"     # Windows应用ID（用于任务栏图标）

# ========================================
# Windows 拖拽常量
# ========================================
WIN_GMEM_MOVEABLE = 0x0002                  # Windows内存分配标志
WIN_WM_DROPFILES = 0x0233                   # Windows拖拽文件消息
WIN_GWL_WNDPROC = -4                        # Windows窗口过程索引

# ========================================
# 延迟设置（毫秒）
# ========================================
DELAY_DROP_REGISTER = 100                   # 拖拽注册延迟
DELAY_UPDATE_AFTER_DROP = 10                # 拖拽后更新延迟

# ========================================
# 拖拽策略
# ========================================
DROP_ONLY_IN_FILE_LIST = True               # 是否仅在“当前选择的文件框”中允许拖拽生效


def get_app_dir():
    """
    获取应用程序目录
    
    在开发环境和打包环境（PyInstaller）中都能正确工作
    
    Returns:
        str: 应用程序根目录路径
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后的环境
        return os.path.dirname(sys.executable)
    # 开发环境
    return os.path.dirname(os.path.abspath(__file__))


def get_icon_path():
    """
    获取图标文件完整路径
    
    Returns:
        str: 图标文件路径
    """
    return os.path.join(get_app_dir(), ICON_FILE_NAME)


def get_groups_file_path():
    """
    获取文件组保存文件完整路径
    
    Returns:
        str: 文件组JSON文件路径
    """
    return os.path.join(get_app_dir(), GROUPS_FILE_NAME)


# ========================================
# UI 文字常量
# ========================================
TEXT_TITLE = "📁 文件批量打开工具"
TEXT_SELECT_FILES = "📝 选择文件"
TEXT_SAVE_GROUP = "💾 保存文件组"
TEXT_REMOVE = "🗑️ 移除"
TEXT_OPEN = "🚀 打开"
TEXT_MY_GROUPS = "📂 我的文件组"
TEXT_CURRENT_FILES = "当前选择的文件"
TEXT_NO_GROUPS = "暂无保存的文件组\n\n选择文件后点击「保存文件组」"
TEXT_SAVE_GROUP_TITLE = "保存文件组"
TEXT_SAVE_GROUP_PROMPT = "请输入文件组名称:"
TEXT_EDIT_GROUP_TITLE = "编辑文件组"
TEXT_EDIT_GROUP_FILES = "文件列表"
TEXT_EDIT_ADD_FILES = "添加文件"
TEXT_EDIT_REMOVE_SELECTED = "删除选中"
TEXT_SAVE = "保存"
TEXT_CANCEL = "取消"
TEXT_DELETE_GROUP_TITLE = "确认删除"
TEXT_DELETE_GROUP_PROMPT = "确定要删除文件组「{}」吗？"
TEXT_EXPAND_ICON = "▶"
TEXT_COLLAPSE_ICON = "▼"
TEXT_CHECK_EXISTS = "✅"
TEXT_CHECK_MISSING = "❌"
