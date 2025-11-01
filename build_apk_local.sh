#!/bin/bash

# 本地APK构建脚本

echo "开始本地APK构建..."

# 设置环境变量
export ANDROID_HOME=$HOME/android-sdk
export ANDROID_SDK_ROOT=$ANDROID_HOME
export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools:$ANDROID_HOME/build-tools

# 创建Android SDK目录
mkdir -p $ANDROID_HOME

# 检查是否已安装命令行工具
if [ ! -d "$ANDROID_HOME/cmdline-tools/latest" ]; then
    echo "安装Android命令行工具..."
    cd /tmp
    wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip -O sdk-tools.zip
    unzip -q sdk-tools.zip -d $ANDROID_HOME/
    mkdir -p $ANDROID_HOME/cmdline-tools/latest
    mv $ANDROID_HOME/cmdline-tools/* $ANDROID_HOME/cmdline-tools/latest/ 2>/dev/null || true
fi

# 安装SDK组件
echo "安装Android SDK组件..."
yes | $ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager --sdk_root=$ANDROID_HOME \
  "platform-tools" \
  "platforms;android-33" \
  "tools"

# 接受许可证
echo "接受Android SDK许可证..."
yes | $ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager --licenses

# 显式安装build-tools
yes | $ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager --sdk_root=$ANDROID_HOME "build-tools;33.0.2"

# 安装Python依赖
echo "安装Python依赖..."
pip3 install --upgrade pip setuptools wheel
pip3 install "Cython>=0.29"
pip3 install "buildozer==1.6.0"
pip3 install "kivy==2.3.0"
pip3 install numpy requests urllib3 pypinyin

# 清理之前的构建
echo "清理之前的构建..."
rm -rf .buildozer
rm -rf bin

# 构建APK
echo "开始构建APK..."
buildozer android debug

echo "构建完成！检查bin目录中的APK文件。"