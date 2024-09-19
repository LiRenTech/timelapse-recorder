import os
import asyncio
import subprocess
from time import perf_counter

from PIL import ImageGrab
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QComboBox,
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer

from assets import assets  # noqa: F401


class ScreenshotApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

        self.output_dir = "output"
        self.current_dir = ""

        self.timer = QTimer(self)  # 动态开启一个Qt定时器
        self.grab_index = 0  # 截图计数器
        self.is_recording = False  # 录制状态
        self.capture_interval = 1000  # 默认间隔1000毫秒
        self.frame_rate = 30  # 默认帧率
        self.speed_rate = 20  # 默认速度倍率
        self.cache_size = 0  # 缓存大小 MB
        self.current_settings = ""  # 当前设置 比如倍率和帧率的序列化信息

    def init_ui(self):
        self.setWindowTitle("延时录屏")
        self.setWindowIcon(QIcon(":/favicon.ico"))
        # 设置最小宽度大小
        self.setMinimumWidth(500)
        layout = QVBoxLayout()

        self.tips_text = QLabel("按下按钮开始录制", self)
        layout.addWidget(self.tips_text)

        self.record_button = QPushButton("开始录制", self)
        self.record_button.clicked.connect(self.toggle_recording)
        layout.addWidget(self.record_button)

        layout.addWidget(QLabel("最终视频倍速：", self))
        self.speed_combo = QComboBox(self)
        self.speed_combo.addItems(
            ["x10", "x20", "x50", "x100", "x200", "x500", "x1000"]
        )
        self.speed_combo.currentIndexChanged.connect(self.update_speed)
        # 设置默认倍速为20
        self.speed_combo.setCurrentIndex(1)
        layout.addWidget(self.speed_combo)

        # 添加下拉框选择帧率
        layout.addWidget(QLabel("最终视频帧率：", self))
        self.frame_rate_combo = QComboBox(self)
        self.frame_rate_combo.addItems(["30帧", "60帧"])
        self.frame_rate_combo.currentIndexChanged.connect(self.update_frame_rate)
        layout.addWidget(self.frame_rate_combo)

        self.setLayout(layout)

    def update_speed(self, index):
        intervals = [10, 20, 50, 100, 200, 500, 1000]  # 毫秒数
        self.speed_rate = intervals[index]

    def update_frame_rate(self, index):
        frame_rates = [30, 60]  # 帧率选项
        self.frame_rate = frame_rates[index]

    async def grab_screenshot(self, file_name="screenshot.png"):
        # 截图并保存
        t1 = perf_counter()
        im = ImageGrab.grab()
        im.save(file_name)
        t2 = perf_counter()
        print(f"截图耗时：{t2 - t1:.2f}秒")

        # 获取截图文件夹大小
        size = os.path.getsize(file_name) / 1024 / 1024
        print(f"截图大小：{size:.2f}MB")
        self.cache_size += size

        # 刷新提示
        seconds = self.grab_index / self.frame_rate
        self.tips_text.setText(
            f"当前设定：{self.current_settings}\n"
            f"已有帧数：{self.grab_index + 1}帧\n"
            f"视频时长：{seconds:.2f}秒\n"
            f"缓存大小：{self.cache_size:.2f}MB"
        )
        self.grab_index += 1

    def images_to_video(self, dir_name, video_name="timelapse.mp4"):
        # 使用ffmpeg将图片合成视频
        command = [
            "ffmpeg",
            "-framerate",
            str(self.frame_rate),  # 使用选定的帧率
            "-i",
            f"{dir_name}/%d.png",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            video_name,
        ]
        subprocess.run(command)
        print(f"视频已保存为 {video_name}")

    def toggle_recording(self):
        if self.is_recording:
            self.stop_screenshots()
        else:
            self.start_screenshots()

    def start_screenshots(self):
        self.is_recording = True
        self.grab_index = 0

        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)

        self.current_dir = f"screenshots-{int(perf_counter())}"
        dir_name = f"{self.output_dir}/{self.current_dir}"
        os.mkdir(dir_name)
        # 设置当前设置
        self.current_settings = f"倍速{self.speed_rate}，帧率{self.frame_rate}帧"

        self.record_button.setText("停止录制")
        self.timer.timeout.connect(
            lambda: asyncio.run(
                self.grab_screenshot(f"{dir_name}/{self.grab_index}.png")
            )
        )
        self.timer.start(
            int(1000 / self.frame_rate * self.speed_rate)
        )  # 使用自定义间隔

    def stop_screenshots(self):
        self.is_recording = False
        self.grab_index = 0
        self.timer.stop()
        self.tips_text.setText("正在生成视频……")
        # 禁用按钮
        self.record_button.setEnabled(False)
        self.record_button.setText("正在生成视频……")

        # 改成红色
        self.tips_text.setStyleSheet("QLabel { color: red; }")
        self.update()

        self.images_to_video(
            f"{self.output_dir}/{self.current_dir}", f"{self.current_dir}.mp4"
        )
        self.tips_text.setText("截图完成并生成视频！")

        # 改成绿色
        self.tips_text.setStyleSheet("QLabel { color: green; }")

        # 更新按钮文本
        self.record_button.setText("开始录制")

        # 删除临时文件夹 output
        for root, dirs, files in os.walk(f"{self.output_dir}", topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(f"{self.output_dir}")

        # 启用按钮
        self.record_button.setEnabled(True)


if __name__ == "__main__":
    app = QApplication([])
    window = ScreenshotApp()
    window.show()
    app.exec_()
