#!/bin/bash

# 构建APK的Docker脚本

echo "修复 python-for-android setup.py 文件..."
python fix_p4a_setup.py

if [ $? -ne 0 ]; then
    echo "修复 python-for-android setup.py 文件失败"
    exit 1
fi

echo "开始构建Docker镜像..."
docker build -t dietplanner-builder .

if [ $? -ne 0 ]; then
    echo "构建Docker镜像失败"
    exit 1
fi

echo "运行构建..."
docker run --rm -v "$(pwd)":/app dietplanner-builder

echo "构建完成"
