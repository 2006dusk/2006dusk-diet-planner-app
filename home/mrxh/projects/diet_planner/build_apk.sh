#!/bin/bash

# 饮食规划应用APK构建脚本
# 适用于WSL环境

echo "开始配置饮食规划应用的APK构建环境..."

# 设置变量
PROJECT_DIR="/home/mrxh/projects/diet_planner"
P4A_DIR="$PROJECT_DIR/.buildozer/android/platform/python-for-android"

# 创建必要的目录
mkdir -p $PROJECT_DIR/.buildozer/android/platform

# 检查是否已存在python-for-android
if [ ! -d "$P4A_DIR" ]; then
    echo "正在下载python-for-android..."
    cd $PROJECT_DIR/.buildozer/android/platform
    wget https://github.com/kivy/python-for-android/archive/master.zip -O p4a.zip
    unzip p4a.zip
    mv python-for-android-master python-for-android
    
    # 初始化git仓库
    cd $P4A_DIR
    git init
    git config user.email "mrxh@example.com"
    git config user.name "mrxh"
    git add .
    git commit -m "Initial commit"
else
    echo "python-for-android已存在，跳过下载"
fi

# 配置buildozer.spec文件
echo "配置buildozer.spec文件..."
cd $PROJECT_DIR

# 备份原始文件
cp buildozer.spec buildozer.spec.bak

# 更新配置
sed -i 's/log_level =.*/log_level = 2/' buildozer.spec
sed -i 's/android.arch =.*/android.archs = arm64-v8a,armeabi-v7a/' buildozer.spec

# 添加p4a配置（如果不存在）
if ! grep -q "p4a.source_dir" buildozer.spec; then
    echo "" >> buildozer.spec
    echo "# 本地python-for-android路径" >> buildozer.spec
    echo "p4a.source_dir = $P4A_DIR" >> buildozer.spec
    echo "p4a.no_git_clone = true" >> buildozer.spec
fi

# 确保[buildozer]部分配置正确
if grep -A 10 "\[buildozer\]" buildozer.spec | grep -q "log_level"; then
    sed -i '/\[buildozer\]/,/^\[.*\]/ s/log_level =.*/log_level = 2/' buildozer.spec
else
    sed -i '/\[buildozer\]/a log_level = 2' buildozer.spec
fi

echo "开始构建APK..."
# 开始构建
~/.local/bin/buildozer android debug

echo "构建完成！如果成功，APK文件将在bin目录中。"