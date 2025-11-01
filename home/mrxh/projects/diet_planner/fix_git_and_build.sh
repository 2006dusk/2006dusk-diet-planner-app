#!/bin/bash

# 修复Git仓库并构建APK的脚本

echo "开始修复Git仓库并构建APK..."

# 设置变量
PROJECT_DIR="/mnt/d/python文件半成品/饮食规划"
P4A_DIR="$PROJECT_DIR/.buildozer/android/platform/python-for-android"

# 进入项目目录
cd "$PROJECT_DIR"

# 修复python-for-android Git仓库
echo "修复python-for-android Git仓库..."

if [ -d "$P4A_DIR" ]; then
    cd "$P4A_DIR"
    
    # 检查是否存在Git仓库
    if [ ! -d ".git" ]; then
        echo "初始化Git仓库..."
        git init
    fi
    
    # 检查是否有远程仓库配置
    if ! git remote -v | grep -q origin; then
        echo "添加远程仓库..."
        git remote add origin https://github.com/kivy/python-for-android.git
    fi
    
    # 检查当前分支状态
    BRANCH=$(git branch --show-current 2>/dev/null)
    if [ -z "$BRANCH" ]; then
        echo "设置默认分支..."
        # 检查是否有提交记录
        if ! git log --oneline -1 >/dev/null 2>&1; then
            # 如果没有提交，创建一个初始提交
            git config user.email "mrxh@example.com"
            git config user.name "mrxh"
            git add .
            git commit -m "Initial commit"
        fi
        
        # 创建并切换到master分支
        git checkout -b master 2>/dev/null || git checkout master
    fi
    
    # 确保远程跟踪分支存在
    git fetch origin master 2>/dev/null || true
    
    echo "Git仓库修复完成"
else
    echo "错误: 未找到python-for-android目录: $P4A_DIR"
    exit 1
fi

# 返回项目目录
cd "$PROJECT_DIR"

# 再次尝试构建
echo "开始APK构建过程..."
buildozer -v android debug

if [ $? -eq 0 ]; then
    echo "APK构建成功完成！"
    echo "APK文件位置: $PROJECT_DIR/bin/"
else
    echo "构建失败，请检查错误日志"
    exit 1
fi