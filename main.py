import os
import asyncio
import subprocess
from time import perf_counter
from PIL import ImageGrab
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel


class ScreenshotApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

        self.output_dir = "output"
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)

        self.current_dir = ""

    def init_ui(self):
        self.setWindowTitle("延时摄影录屏工具")
        # 设置最小宽度大小
        self.setMinimumWidth(400)
        layout = QVBoxLayout()

        self.label = QLabel("按下按钮开始录制", self)
        layout.addWidget(self.label)

        self.start_button = QPushButton("开始录制", self)
        self.start_button.clicked.connect(self.start_screenshots)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("停止录制", self)
        self.stop_button.clicked.connect(self.stop_screenshots)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)

    async def grab_screenshot(self, file_name="screenshot.png"):
        # 截图并保存
        t1 = perf_counter()
        im = ImageGrab.grab()
        im.save(file_name)
        t2 = perf_counter()
        print(f"截图耗时：{t2 - t1:.2f}秒")

    def images_to_video(self, dir_name, video_name="timelapse.mp4"):
        # 使用ffmpeg将图片合成视频
        command = [
            "ffmpeg",
            "-framerate",
            "30",
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

    def start_screenshots(self):
        self.label.setText("正在截图...")

        self.current_dir = f"screenshots-{int(perf_counter())}"
        dir_name = f"{self.output_dir}/{self.current_dir}"
        os.mkdir(dir_name)

        loop = asyncio.get_event_loop()

        async def take_screenshots():
            for i in range(50):
                await self.grab_screenshot(f"{dir_name}/{i + 1}.png")
                await asyncio.sleep(1)

        loop.run_until_complete(take_screenshots())

    def stop_screenshots(self):
        self.images_to_video(f"{self.output_dir}/{self.current_dir}")
        self.label.setText("截图完成并生成视频！")
        pass


if __name__ == "__main__":
    app = QApplication([])
    window = ScreenshotApp()
    window.show()
    app.exec_()
