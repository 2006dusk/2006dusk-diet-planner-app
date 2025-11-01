#!/bin/bash

# 完整的构建环境设置脚本

echo "开始设置完整的构建环境..."

# 更新系统
echo "更新系统包..."
sudo apt update

# 安装基本依赖
echo "安装基本依赖..."
sudo apt install -y build-essential libffi-dev libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev libncurses5-dev libncursesw5-dev liblzma-dev libxml2-dev libxslt1-dev libcurl4-openssl-dev libexpat1-dev
sudo apt install -y git wget libgl1 libglx-dev libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1
sudo apt install -y openjdk-17-jdk unzip

# 设置环境变量
export ANDROID_HOME=$HOME/android-sdk
export ANDROID_SDK_ROOT=$ANDROID_HOME
export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools:$ANDROID_HOME/build-tools

# 创建目录
mkdir -p $ANDROID_HOME

# 检查是否已安装SDK工具
if [ ! -f "$ANDROID_HOME/cmdline-tools/bin/sdkmanager" ]; then
    echo "下载并安装Android SDK命令行工具..."
    cd $HOME
    wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip -O sdk-tools.zip
    mkdir -p $ANDROID_HOME/cmdline-tools
    unzip -q sdk-tools.zip -d $ANDROID_HOME/cmdline-tools/
    # 重新命名目录以符合sdkmanager期望的结构
    mv $ANDROID_HOME/cmdline-tools/cmdline-tools $ANDROID_HOME/cmdline-tools/latest
fi

# 安装必要的SDK组件
echo "安装Android SDK组件..."
yes | $ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager --sdk_root=$ANDROID_HOME "platform-tools" "build-tools;33.0.2" "platforms;android-33" "tools"

# 安装Python依赖
echo "安装Python构建依赖..."
pip3 install --upgrade pip setuptools wheel
pip3 install "Cython>=0.29"
pip3 install "buildozer==1.6.0" 
pip3 install "kivy==2.3.0"
pip3 install numpy requests urllib3 pypinyin

# 清理之前的构建
echo "清理之前的构建..."
rm -rf .buildozer
rm -rf bin

echo "环境设置完成！"
echo "现在可以运行以下命令来构建APK:"
echo "buildozer android debug"