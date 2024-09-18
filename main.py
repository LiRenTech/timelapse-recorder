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
        self.setWindowTitle("延时录屏")
        # 设置最小宽度大小
        self.setMinimumWidth(500)
        layout = QVBoxLayout()

        self.tips_text = QLabel("按下按钮开始录制", self)
        layout.addWidget(self.tips_text)

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
        self.tips_text.setText("正在截图...")

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
        self.tips_text.setText("正在生成视频……")
        # 改成红色
        self.tips_text.setStyleSheet("QLabel { color: red; }")
        self.images_to_video(f"{self.output_dir}/{self.current_dir}", f"{self.current_dir}.mp4")
        self.tips_text.setText("截图完成并生成视频！")
        # 改成绿色
        self.tips_text.setStyleSheet("QLabel { color: green; }")
        
        # 删除临时文件夹
        # os.rmdir(f"{self.output_dir}/{self.current_dir}")  # 报错，目录不是空的

        # 递归删除
        for root, dirs, files in os.walk(f"{self.output_dir}/{self.current_dir}", topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(f"{self.output_dir}/{self.current_dir}")

        pass


if __name__ == "__main__":
    app = QApplication([])
    window = ScreenshotApp()
    window.show()
    app.exec_()
