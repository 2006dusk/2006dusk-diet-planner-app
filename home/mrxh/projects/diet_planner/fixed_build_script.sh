#!/bin/bash

# 修复版饮食规划应用APK构建脚本 (WSL版本)
# 解决构建失败问题

echo "开始修复并配置饮食规划应用的APK构建环境..."

# 设置变量
PROJECT_DIR="/mnt/d/python文件半成品/饮食规划"
BUILD_DIR="$PROJECT_DIR/.buildozer/android/platform"
P4A_DIR="$BUILD_DIR/python-for-android"

# 进入项目目录 (Windows路径)
cd "$PROJECT_DIR"

# 验证当前目录
echo "当前工作目录: $(pwd)"

# 清理之前的构建
echo "清理之前的构建..."
buildozer android clean

# 配置buildozer.spec文件
echo "配置buildozer.spec文件..."
# 更新日志级别
sed -i 's/log_level =.*/log_level = 2/' buildozer.spec

# 确保架构配置正确
sed -i 's/android.archs =.*/android.archs = arm64-v8a,armeabi-v7a/' buildozer.spec
sed -i 's/android.arch =.*/android.archs = arm64-v8a,armeabi-v7a/' buildozer.spec

# 添加p4a配置（如果不存在）
if ! grep -q "p4a.source_dir" buildozer.spec; then
    echo "" >> buildozer.spec
    echo "# 本地python-for-android路径" >> buildozer.spec
    echo "p4a.source_dir = $P4A_DIR" >> buildozer.spec
fi

if ! grep -q "p4a.no_git_clone" buildozer.spec; then
    echo "p4a.no_git_clone = true" >> buildozer.spec
fi

# 确保[buildozer]部分配置正确
if grep -A 10 "\[buildozer\]" buildozer.spec | grep -q "log_level"; then
    sed -i '/\[buildozer\]/,/^\[.*\]/ s/log_level =.*/log_level = 2/' buildozer.spec
else
    sed -i '/\[buildozer\]/a log_level = 2' buildozer.spec
fi

# 配置Git使用国内镜像源
echo "配置Git使用国内镜像源..."
git config --global url."https://ghproxy.com/https://github.com/".insteadOf "https://github.com/"
git config --global http.sslVerify false

# 预安装Cython (重要步骤，可以避免后续构建问题)
echo "安装/升级Cython..."
pip3 install --upgrade Cython

# 检查并设置python-for-android
echo "检查python-for-android设置..."
if [ ! -d "$P4A_DIR" ]; then
    echo "创建python-for-android目录..."
    mkdir -p "$P4A_DIR"
fi

cd "$P4A_DIR"

# 如果目录为空，初始化git仓库
if [ -z "$(ls -A .)" ]; then
    echo "初始化python-for-android git仓库..."
    git init
    git remote add origin https://github.com/kivy/python-for-android.git
    git config user.email "mrxh@example.com"
    git config user.name "mrxh"
fi

# 添加虚拟远程地址（解决之前的Git问题）
if ! git remote -v | grep -q origin; then
    echo "添加虚拟远程地址..."
    git remote add origin https://github.com/kivy/python-for-android.git
fi

# 返回项目目录
cd "$PROJECT_DIR"

# 创建必要的目录
SDL2_IMAGE_DIR="$BUILD_DIR/build-arm64-v8a_armeabi-v7a/build/bootstrap_builds/sdl2/jni/SDL2_image/external"
mkdir -p "$SDL2_IMAGE_DIR"

# 定义带重试功能的下载函数
download_with_retry() {
    local url=$1
    local output=$2
    local dirname=$3
    local max_retries=5
    local retry_count=0
    
    echo "下载 $dirname..."
    
    while [ $retry_count -lt $max_retries ]; do
        echo "尝试下载 $url (第 $((retry_count+1)) 次)..."
        wget --timeout=60 --tries=1 "$url" -O "$output"
        
        if [ $? -eq 0 ] && [ -f "$output" ]; then
            echo "下载成功: $output"
            # 解压文件
            unzip -q "$output" -d .
            # 重命名目录
            if [ -d "${dirname}-main" ]; then
                mv "${dirname}-main" "$dirname"
            elif [ -d "${dirname}-4.5.0" ]; then
                mv "${dirname}-4.5.0" "$dirname"
            fi
            rm "$output"
            return 0
        else
            echo "下载失败，等待5秒后重试..."
            retry_count=$((retry_count + 1))
            sleep 5
        fi
    done
    
    echo "下载 $dirname 失败，已达到最大重试次数"
    return 1
}

# 手动下载SDL2_image依赖库
cd "$SDL2_IMAGE_DIR"

# 清理现有文件
rm -rf jpeg png tiff webp

# 下载JPEG库
if [ ! -d "jpeg" ]; then
    download_with_retry "https://ghproxy.com/https://github.com/libsdl-org/jpeg/archive/refs/heads/main.zip" "jpeg.zip" "jpeg"
fi

# 下载PNG库
if [ ! -d "png" ]; then
    download_with_retry "https://ghproxy.com/https://github.com/libsdl-org/png/archive/refs/heads/main.zip" "png.zip" "png"
fi

# 下载TIFF库
if [ ! -d "tiff" ]; then
    download_with_retry "https://ghproxy.com/https://github.com/libsdl-org/tiff/archive/refs/tags/v4.5.0.zip" "tiff.zip" "tiff"
fi

# 下载WEBP库
if [ ! -d "webp" ]; then
    download_with_retry "https://ghproxy.com/https://github.com/libsdl-org/webp/archive/refs/heads/main.zip" "webp.zip" "webp"
fi

# 返回项目目录
cd "$PROJECT_DIR"

# 检查所有依赖是否已下载
echo "检查依赖完整性..."
cd "$SDL2_IMAGE_DIR"
MISSING_DEPS=0
for dep in jpeg png tiff webp; do
    if [ ! -d "$dep" ]; then
        echo "错误: 缺少依赖 $dep"
        MISSING_DEPS=1
    else
        echo "依赖 $dep 已就位"
    fi
done

if [ $MISSING_DEPS -eq 1 ]; then
    echo "警告: 一些依赖项缺失，可能会导致构建失败"
fi

# 返回项目目录
cd "$PROJECT_DIR"

# 开始构建APK
echo "开始构建APK..."
echo "使用国内镜像源以提高下载速度..."

buildozer android debug

if [ $? -eq 0 ]; then
    echo "APK构建成功完成！"
    echo "APK文件位置: $PROJECT_DIR/bin/"
else
    echo "构建失败，请检查错误日志"
    exit 1
fi