import os
import asyncio
from time import perf_counter
import subprocess

from PIL import ImageGrab


async def grab_screenshot(file_name="screenshot.png"):
    # 截图并保存
    t1 = perf_counter()
    im = ImageGrab.grab()
    im.save(file_name)
    t2 = perf_counter()
    print(f"截图耗时：{t2 - t1:.2f}秒")
    # 经测试大约耗时0.3秒


def images_to_video(dir_name, video_name="timelapse.mp4"):
    # 将图片合成视频
    # 使用ffmpeg将图片合成视频
    command = [
        "ffmpeg",
        "-framerate",
        "30",  # 设置帧率
        "-i",
        f"{dir_name}/%d.png",  # 输入文件的路径
        "-c:v",
        "libx264",  # 设置视频编码格式
        "-pix_fmt",
        "yuv420p",  # 设置像素格式
        video_name,  # 输出视频文件名
    ]

    # 调用ffmpeg命令
    subprocess.run(command)
    print(f"视频已保存为 {video_name}")
    pass


async def main():
    input("按任意键开始截图...")

    # 先在当前文件夹下创建一个文件夹
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    # 文件夹名字以时间格式
    dir_name = f"screenshots-{int(perf_counter())}"

    if not os.path.exists(f"{output_dir}/{dir_name}"):
        os.mkdir(dir_name)

    for i in range(10):
        print(f"第{i+1}次截图")
        asyncio.create_task(grab_screenshot(f"{dir_name}/{i+1}.png"))
        await asyncio.sleep(1)

    pass


if __name__ == "__main__":
    asyncio.run(main())
