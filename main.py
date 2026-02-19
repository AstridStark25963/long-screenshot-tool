import ctypes
from ui import FloatingUI


def setup_dpi_awareness():
    """解决 Windows 系统下 Tkinter 坐标与实际像素不匹配的问题"""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except AttributeError:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


if __name__ == "__main__":
    # 1. 初始化 DPI 环境
    setup_dpi_awareness()

    # 2. 启动悬浮 UI 界面
    app = FloatingUI()
    app.root.mainloop()