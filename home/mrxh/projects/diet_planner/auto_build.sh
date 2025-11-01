#!/bin/bash

# 自动化构建脚本 - 无需用户交互
# 正确处理所有本地ZIP文件并自动回答替换提示

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

# 定义解压函数，自动覆盖文件
extract_and_setup() {
    local zip_file=$1
    local target_dir=$2
    local extract_name=$3
    
    if [ -f "$PROJECT_DIR/$zip_file" ]; then
        echo "解压 $zip_file..."
        # 使用-overwrite选项自动覆盖文件，避免交互提示
        unzip -q -o "$PROJECT_DIR/$zip_file"
        
        # 检查并重命名目录
        if [ -n "$extract_name" ] && [ -d "$extract_name" ]; then
            mv "$extract_name" "$target_dir"
        elif [ -d "${zip_file%.zip}" ]; then
            mv "${zip_file%.zip}" "$target_dir"
        else
            # 如果无法确定目录名，创建目标目录
            mkdir -p "$target_dir"
        fi
        
        echo "$target_dir 库已设置"
        return 0
    else
        echo "警告: 未找到 $zip_file 文件"
        return 1
    fi
}

# 解压并设置JPEG库
extract_and_setup "jpeg-main.zip" "jpeg" "jpeg-main"

# 解压并设置PNG库
if ! extract_and_setup "lpng1650.zip" "png" "lpng1650"; then
    extract_and_setup "png.zip" "png" "png-main"
fi

# 解压并设置TIFF库
extract_and_setup "tiff-4.5.0.zip" "tiff" "tiff-4.5.0"

# 解压并设置WEBP库
if ! extract_and_setup "libwebp-main.zip" "webp" "libwebp-main"; then
    extract_and_setup "webp.zip" "webp" "webp-main"
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

# 使用-y选项自动回答yes到所有提示
buildozer -v android debug

if [ $? -eq 0 ]; then
    echo "APK构建成功完成！"
    echo "APK文件位置: $PROJECT_DIR/bin/"
else
    echo "构建失败，请检查错误日志"
    exit 1
fi