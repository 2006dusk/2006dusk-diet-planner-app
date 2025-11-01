#!/bin/bash

# 下载并设置真实的python-for-android

echo "下载并设置真实的python-for-android..."

# 设置变量
PROJECT_DIR="/mnt/d/python文件半成品/饮食规划"
P4A_DIR="$PROJECT_DIR/.buildozer/android/platform/python-for-android"

# 备份我们当前的模拟版本
if [ -d "$P4A_DIR" ]; then
    echo "备份当前的模拟版本..."
    mv "$P4A_DIR" "${P4A_DIR}_backup"
fi

# 克隆真实的python-for-android仓库
echo "克隆真实的python-for-android仓库..."
mkdir -p "$P4A_DIR"
cd "$P4A_DIR"
git clone https://github.com/kivy/python-for-android.git .
# 切换到稳定版本
git checkout stable

# 安装python-for-android
echo "安装python-for-android..."
pip3 install -e .

# 创建符号链接以确保路径正确
cd "$PROJECT_DIR"
ln -sf "$P4A_DIR" .buildozer/android/platform/python-for-android

echo "真实的python-for-android设置完成!"
echo "现在可以尝试运行构建命令来生成真正的APK:"
echo "buildozer android debug"

echo ""
echo "注意事项:"
echo "1. 首次构建可能需要较长时间（10-30分钟）"
echo "2. 需要下载大量依赖项，确保网络连接稳定"
echo "3. 如果在国内，建议配置镜像源以加速下载"
echo "4. 构建过程中可能会提示安装额外的系统依赖"