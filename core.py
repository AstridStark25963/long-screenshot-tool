# 文件名: core.py
import cv2
import numpy as np
import mss
import time


class ScreenCapturer:
    """负责高频屏幕抓取与静止帧过滤的模块"""

    def __init__(self, fps=15):
        self.fps = fps
        self.frames = []
        self.is_recording = False

    def start_capture(self, region):
        self.is_recording = True
        self.frames = []

        with mss.mss() as sct:
            while self.is_recording:
                sct_img = sct.grab(region)
                frame = np.array(sct_img)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

                if self.frames:
                    diff = cv2.absdiff(frame, self.frames[-1])
                    if np.mean(diff) > 1.0:
                        self.frames.append(frame)
                else:
                    self.frames.append(frame)

                time.sleep(1.0 / self.fps)

    def stop_capture(self):
        self.is_recording = False
        return self.frames


class ImageStitcher:
    """负责核心图像特征匹配与拼接的模块"""

    def __init__(self, template_height=100, bottom_margin=0):
        self.template_height = template_height
        self.bottom_margin = bottom_margin

        # --- 新增 progress_callback 回调参数 ---

    def stitch(self, frames, progress_callback=None):
        if not frames or len(frames) < 2:
            if progress_callback: progress_callback(100)
            return frames[0] if frames else None

        result_img = frames[0]
        prev_frame = frames[0]
        total_steps = len(frames) - 1  # 总共需要匹配的次数

        for i in range(1, len(frames)):
            curr_frame = frames[i]
            y_end = prev_frame.shape[0] - self.bottom_margin
            y_start = y_end - self.template_height

            if y_start < 0:
                return result_img

            template = prev_frame[y_start:y_end, :]
            res = cv2.matchTemplate(curr_frame, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)

            if max_val > 0.8:
                match_y = max_loc[1]
                new_content_start = match_y + self.template_height
                new_content = curr_frame[new_content_start:, :]

                if new_content.shape[0] > 0:
                    result_img = np.vstack((result_img, new_content))
                    prev_frame = curr_frame

                    # --- 实时计算并返回进度 ---
            if progress_callback:
                progress = int((i / total_steps) * 100)
                progress_callback(progress)

        if progress_callback: progress_callback(100)
        return result_img