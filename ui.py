# 文件名: ui.py
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import cv2
import os
from datetime import datetime
from PIL import Image  # 新增：用于加载真实的图像图标

from core import ScreenCapturer, ImageStitcher

ctk.set_appearance_mode("Dark")


class RegionSelector:
    """提供一个全屏半透明遮罩，用于框选区域"""

    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.attributes('-alpha', 0.3)
        self.top.attributes('-fullscreen', True)
        self.top.attributes('-topmost', True)
        self.top.config(cursor="cross")

        self.canvas = tk.Canvas(self.top, cursor="cross", bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.start_x = self.start_y = 0
        self.rect = None
        self.region = None

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        # 选框颜色改为 Win11 蓝
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='#60CDFF', width=2, fill="#202020"
        )

    def on_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        x1, x2 = sorted([self.start_x, event.x])
        y1, y2 = sorted([self.start_y, event.y])
        self.region = {'left': x1, 'top': y1, 'width': x2 - x1, 'height': y2 - y1}
        self.top.destroy()

    def get_region(self):
        self.top.wait_window()
        return self.region


class FloatingUI:
    """Windows 11 Fluent Design 风格主控界面"""

    def __init__(self):
        self.root = ctk.CTk()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.95)  # 稍微提高一点不透明度，更有质感

        transparent_color = "#000001"
        self.root.configure(fg_color=transparent_color)
        self.root.wm_attributes("-transparentcolor", transparent_color)

        # 稍微加高窗口，给图标留足呼吸空间
        screen_width = self.root.winfo_screenwidth()
        self.root.geometry(f"360x115+{screen_width // 2 - 180}+20")

        self.capturer = ScreenCapturer(fps=15)
        self.stitcher = ImageStitcher(template_height=100)
        self.current_region = None
        self.capture_thread = None

        self.setup_ui()

    def _load_icon(self, filename):
        """安全加载图标的辅助函数"""
        base_path = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_path, "icons", filename)

        if os.path.exists(icon_path):
            # CTkImage 可以在高分屏下保持清晰
            return ctk.CTkImage(light_image=Image.open(icon_path),
                                dark_image=Image.open(icon_path),
                                size=(22, 22))
        return None

    def setup_ui(self):
        # 1. Win11 风格背景：深空灰 (#202020)，配上极细的亮色边框模拟高光
        self.bg_frame = ctk.CTkFrame(self.root, corner_radius=8,
                                     fg_color="#202020", bg_color="#000001",
                                     border_width=1, border_color="#333333")
        self.bg_frame.pack(fill="both", expand=True, padx=2, pady=2)

        self.upper_frame = ctk.CTkFrame(self.bg_frame, fg_color="transparent")
        self.upper_frame.pack(side="top", fill="x", padx=10, pady=(10, 5))

        # 可拖动把手 (修改为更柔和的颜色)
        self.drag_label = ctk.CTkLabel(self.upper_frame, text="⠿", text_color="#555555", cursor="fleur", width=15,
                                       font=("Arial", 16))
        self.drag_label.pack(side="left", padx=(0, 10))

        # 绑定全新的、基于绝对坐标的防抖拖动逻辑
        self.drag_label.bind("<ButtonPress-1>", self.start_move)
        self.drag_label.bind("<B1-Motion>", self.do_move)

        # 2. 封装图文复合按钮生成器
        def create_fluent_btn(parent, icon_file, fallback_char, text, cmd, is_close=False):
            img = self._load_icon(icon_file)
            # 如果有图，就只显示传进来的纯文字，并把图片放在文字正上方 (compound="top")
            # 如果没图，就用回字符画模式兜底
            display_text = text if img else f"{fallback_char}\n{text}"

            # Win11 按钮平时是融入背景的 (transparent)，悬浮时才亮起底色
            hover_color = "#C42B1C" if is_close else "#323232"

            btn = ctk.CTkButton(parent, text=display_text, image=img, compound="top",
                                command=cmd, fg_color="transparent", hover_color=hover_color,
                                text_color="#E3E3E3", width=60, height=55, corner_radius=6,
                                font=("Microsoft YaHei UI", 11))
            return btn

        # 3. 实例化四大金刚键
        self.btn_select = create_fluent_btn(self.upper_frame, "crop.png", "✂", "框选", self.do_select)
        self.btn_select.pack(side="left", padx=5)

        self.btn_record = create_fluent_btn(self.upper_frame, "record.png", "●", "录制", self.start_record)
        self.btn_record.configure(state="disabled")
        self.btn_record.pack(side="left", padx=5)

        self.btn_stop = create_fluent_btn(self.upper_frame, "stop.png", "■", "生成", self.stop_and_stitch)
        self.btn_stop.configure(state="disabled")
        self.btn_stop.pack(side="left", padx=5)

        self.btn_quit = create_fluent_btn(self.upper_frame, "close.png", "✖", "关闭", self.root.quit, is_close=True)
        # 用 expand 让关闭按钮靠右对齐，更符合系统习惯
        self.btn_quit.pack(side="right", padx=5)

        # Win11 风格的极细分割线
        self.separator = ctk.CTkFrame(self.bg_frame, height=1, fg_color="#333333")
        self.separator.pack(fill="x", padx=15, pady=(2, 4))

        self.lower_frame = ctk.CTkFrame(self.bg_frame, fg_color="transparent")
        self.lower_frame.pack(side="bottom", fill="x", padx=15, pady=(0, 10))

        # 4. 进度条改造：彻底移除绿色，采用 Win11 核心亮蓝色 (#60CDFF)
        self.progress_bar = ctk.CTkProgressBar(self.lower_frame, height=4, corner_radius=2,
                                               fg_color="#1E1E1E", progress_color="#60CDFF")
        self.progress_bar.pack(fill="x", expand=True)
        self.progress_bar.set(0.0)

        # --- 修复后的丝滑拖动逻辑 ---

    def start_move(self, event):
        # 获取鼠标在整个屏幕上的绝对物理坐标
        self.start_x = event.x_root
        self.start_y = event.y_root
        # 记录点击瞬间，窗口自身的绝对物理坐标
        self.win_x = self.root.winfo_x()
        self.win_y = self.root.winfo_y()

    def do_move(self, event):
        # 计算鼠标在屏幕上移动的绝对偏差
        deltax = event.x_root - self.start_x
        deltay = event.y_root - self.start_y
        # 将偏差加到初始窗口位置上
        self.root.geometry(f"+{self.win_x + deltax}+{self.win_y + deltay}")

    # --- 业务逻辑配合 UI 颜色的微调 ---
    def do_select(self):
        self.root.attributes('-alpha', 0.0)
        selector = RegionSelector(self.root)
        self.current_region = selector.get_region()
        self.root.attributes('-alpha', 0.95)

        if self.current_region and self.current_region['width'] > 50:
            # 选中后，让录制按钮亮起 Win11 的系统主色调（深海蓝）
            self.btn_record.configure(state="normal", fg_color="#005FB8", hover_color="#0078D4")
            self.btn_select.configure(text="重新框选" if self._load_icon("crop.png") else "✂\n重选")
            self.progress_bar.set(0.0)
        else:
            self.current_region = None

    def start_record(self):
        self.btn_select.configure(state="disabled")
        # 录制中，变为深灰色融入背景
        self.btn_record.configure(state="disabled", fg_color="transparent")
        # 生成按钮亮起，提醒用户点击
        self.btn_stop.configure(state="normal", fg_color="#005FB8", hover_color="#0078D4")
        self.progress_bar.set(0.0)

        self.capture_thread = threading.Thread(target=self.capturer.start_capture, args=(self.current_region,))
        self.capture_thread.start()

    def stop_and_stitch(self):
        self.btn_stop.configure(state="disabled", fg_color="transparent")
        frames = self.capturer.stop_capture()

        stitch_thread = threading.Thread(target=self._process_stitching, args=(frames,))
        stitch_thread.start()

    def _process_stitching(self, frames):
        if len(frames) > 0:
            final_image = self.stitcher.stitch(frames, progress_callback=self._update_progress)

            if final_image is not None:
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"Screenshot_{timestamp}.png"
                save_path = os.path.join(os.getcwd(), filename)
                cv2.imwrite(save_path, final_image)

        self.root.after(0, self._reset_ui)

    def _update_progress(self, val):
        self.root.after(0, lambda: self.progress_bar.set(val / 100.0))

    def _reset_ui(self):
        text_sel = "框选" if self._load_icon("crop.png") else "✂\n框选"
        text_rec = "录制" if self._load_icon("record.png") else "●\n录制"
        text_stp = "生成" if self._load_icon("stop.png") else "■\n生成"

        self.btn_select.configure(state="normal", text=text_sel)
        self.btn_record.configure(state="normal", text=text_rec, fg_color="transparent")
        self.btn_stop.configure(state="disabled", text=text_stp, fg_color="transparent")