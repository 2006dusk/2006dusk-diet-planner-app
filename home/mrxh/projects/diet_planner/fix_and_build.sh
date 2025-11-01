#!/bin/bash

# 直接使用本地资源的构建脚本 (修复版)
# 正确处理所有本地ZIP文件

echo "开始使用本地资源构建APK..."

# 设置变量 (直接使用当前目录)
PROJECT_DIR="/mnt/d/python文件半成品/饮食规划"
BUILD_DIR="$PROJECT_DIR/.buildozer/android/platform"
P4A_DIR="$BUILD_DIR/python-for-android"

# 进入项目目录
cd "$PROJECT_DIR"
echo "当前工作目录: $(pwd)"

# 配置Git（基本配置）
echo "配置Git..."
git config --global http.sslVerify false

# 预安装Cython
echo "安装/升级Cython..."
pip3 install --upgrade Cython

# 设置SDL2_image依赖库
SDL2_IMAGE_DIR="$BUILD_DIR/build-arm64-v8a_armeabi-v7a/build/bootstrap_builds/sdl2/jni/SDL2_image/external"
mkdir -p "$SDL2_IMAGE_DIR"

echo "设置SDL2_image依赖库..."
cd "$SDL2_IMAGE_DIR"

# 清理现有文件
rm -rf jpeg png tiff webp

# 解压并设置JPEG库
if [ -f "$PROJECT_DIR/jpeg-main.zip" ]; then
    echo "解压JPEG库..."
    unzip -q "$PROJECT_DIR/jpeg-main.zip"
    mv jpeg-main jpeg
    echo "JPEG库已设置"
else
    echo "警告: 未找到jpeg-main.zip文件"
fi

# 解压并设置PNG库
if [ -f "$PROJECT_DIR/lpng1650.zip" ]; then
    echo "解压PNG库..."
    unzip -q "$PROJECT_DIR/lpng1650.zip"
    mv lpng1650 png
    echo "PNG库已设置"
elif [ -f "$PROJECT_DIR/png.zip" ]; then
    echo "解压PNG库 (备用文件)..."
    unzip -q "$PROJECT_DIR/png.zip"
    # 检查解压后的目录名
    if [ -d "png-main" ]; then
        mv png-main png
    else
        # 如果没有特定目录，创建一个
        mkdir -p png
    fi
    echo "PNG库已设置 (备用文件)"
else
    echo "错误: 未找到PNG相关的zip文件"
fi

# 解压并设置TIFF库
if [ -f "$PROJECT_DIR/tiff-4.5.0.zip" ]; then
    echo "解压TIFF库..."
    unzip -q "$PROJECT_DIR/tiff-4.5.0.zip"
    mv tiff-4.5.0 tiff
    echo "TIFF库已设置"
else
    echo "警告: 未找到tiff-4.5.0.zip文件"
fi

# 解压并设置WEBP库
if [ -f "$PROJECT_DIR/libwebp-main.zip" ]; then
    echo "解压WEBP库..."
    unzip -q "$PROJECT_DIR/libwebp-main.zip"
    mv libwebp-main webp
    echo "WEBP库已设置"
elif [ -f "$PROJECT_DIR/webp.zip" ]; then
    echo "解压WEBP库 (备用文件)..."
    unzip -q "$PROJECT_DIR/webp.zip"
    # 检查解压后的目录名
    if [ -d "webp-main" ]; then
        mv webp-main webp
    else
        # 如果没有特定目录，创建一个
        mkdir -p webp
    fi
    echo "WEBP库已设置 (备用文件)"
else
    echo "错误: 未找到WEBP相关的zip文件"
fi

# 检查所有依赖是否已设置
echo "检查依赖完整性..."
MISSING_DEPS=0
for dep in jpeg png tiff webp; do
    if [ ! -d "$dep" ] || [ -z "$(ls -A "$dep")" ]; then
        echo "错误: 缺少依赖 $dep"
        MISSING_DEPS=1
    else
        echo "依赖 $dep 已就位"
    fi
done

if [ $MISSING_DEPS -eq 1 ]; then
    echo "错误: 一些依赖项缺失，无法继续构建"
    exit 1
fi

echo "所有依赖已正确设置!"

# 返回项目目录并开始构建
cd "$PROJECT_DIR"
echo "开始APK构建过程..."

buildozer android debug

if [ $? -eq 0 ]; then
    echo "APK构建成功完成！"
    echo "APK文件位置: $PROJECT_DIR/bin/"
else
    echo "构建失败，请检查错误日志"
    exit 1
fi