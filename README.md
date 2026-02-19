# Long Screenshot Tool

**Long Screenshot Tool** 是一款专为 Windows 11 设计的现代化长截图工具。它通过高频自适应抓帧技术和 OpenCV 图像拼接算法，解决了网页、文档、代码长图截取的痛点。

![Version](https://img.shields.io/badge/version-v1.0.0-orange.svg)
![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.9.0+-white?logo=opencv&logoColor=white&color=5C3EE8)

---

### ✨ 特性预览

- **Win11 流畅设计**：基于微软 Fluent Design 语言，支持磨砂玻璃质感与暗黑模式。
- **智能拼接算法**：内置 OpenCV 模板匹配引擎，自动过滤滚动时的静止帧，拼接天衣无缝。
- **无冲突悬浮 UI**：抛弃传统全局快捷键，采用不占空间的悬浮条交互，支持自由拖拽。
- **高 DPI 感知**：完美适配 4K 屏幕与 Windows 系统缩放，所见即所得。
- **极致性能**：采用 Nuitka 编译为机器码，双击秒开，告别 Python 打包的臃肿感。

### 🛠️ 如何使用

1. **框选**：点击“框选”按钮，在屏幕上画出你想要截取的区域。
2. **录制**：点击“录制”，开始平滑滚动你的页面（网页、PDF、Excel 等）。
3. **生成**：滚动结束后点击“生成”，进度条读满后，长图将自动保存至软件目录。

### 📦 安装说明

前往 [Releases](https://github.com/AstridStark25963/long-screenshot-tool/releases/tag/v1.0) 下载最新的 `lst_setup_v1.0.exe`，按照向导安装即可。

### 👨‍💻 开发环境
- **Language**: Python 3.12+
- **GUI Framework**: CustomTkinter
- **Core Engine**: OpenCV / NumPy / MSS
- **Compiler**: Nuitka (C-compiled)
- **Installer**: Inno Setup 6
