#!/bin/bash

# 简单直接的修复脚本

echo "修复python-for-android Git仓库配置..."

# 设置变量
PROJECT_DIR="/mnt/d/python文件半成品/饮食规划"
P4A_DIR="$PROJECT_DIR/.buildozer/android/platform/python-for-android"

# 检查并创建目录
if [ ! -d "$P4A_DIR" ]; then
    echo "创建目录: $P4A_DIR"
    mkdir -p "$P4A_DIR"
fi

# 进入p4a目录
cd "$P4A_DIR"

# 初始化Git仓库（如果不存在）
if [ ! -d ".git" ]; then
    echo "初始化Git仓库..."
    git init
fi

# 设置基本的Git配置
git config user.email "mrxh@example.com"
git config user.name "mrxh"

# 添加远程仓库
git remote remove origin 2>/dev/null
git remote add origin https://github.com/kivy/python-for-android.git

# 创建一个提交（如果还没有）
if ! git log --oneline -1 >/dev/null 2>&1; then
    echo "创建初始提交..."
    touch README.md
    git add README.md
    git commit -m "Initial commit"
fi

# 确保有一个分支
git checkout -b master 2>/dev/null || git checkout master

echo "Git仓库配置完成!"

# 返回项目目录
cd "$PROJECT_DIR"

echo "现在你可以尝试运行构建命令:"
echo "buildozer android debug"