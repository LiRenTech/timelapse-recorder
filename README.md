

# 延时摄影录屏工具

## 用途

用于技术区Up主记录某个长时间的加速录像

## 使用方法

需要自行安装ffmpeg并配置环境变量

## 开发相关：

此项目为LiRen团队开源项目，贡献代码前建议阅读开发规范文档中的python内容：https://liren.zty012.de/

更新 assets 资源文件指令

```commandline
pyrcc5 -o assets/assets.py assets/image.qrc
```

打包指令

```commandline
windows:
pyinstaller --onefile --windowed --icon=./assets/favicon.ico main.py -n timelapse-recorder
```