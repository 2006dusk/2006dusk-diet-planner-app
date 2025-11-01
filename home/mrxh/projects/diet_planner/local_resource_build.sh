#!/bin/bash

# 优化版饮食规划应用APK构建脚本 (WSL版本)
# 充分利用本地资源，避免不必要的网络下载

echo "开始配置饮食规划应用的APK构建环境..."

# 设置变量 (使用当前目录，而不是复制到其他位置)
PROJECT_DIR="/mnt/d/python文件半成品/饮食规划"
BUILD_DIR="$PROJECT_DIR/.buildozer/android/platform"
P4A_DIR="$BUILD_DIR/python-for-android"

# 进入项目目录
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

# 配置Git
echo "配置Git..."
# 清除可能存在的冲突配置
git config --global --unset url."https://ghproxy.com/https://github.com/".insteadOf 2>/dev/null || true
git config --global --unset url."https://mirrors.tuna.tsinghua.edu.cn/git/".insteadOf 2>/dev/null || true

# 禁用SSL验证以解决SSL连接问题
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

# 定义使用本地文件的函数
use_local_file() {
    local filename=$1
    local dirname=$2
    local source_path="/mnt/d/python文件半成品/饮食规划/$filename"
    
    echo "检查本地文件: $filename"
    
    if [ -f "$source_path" ] && [ -s "$source_path" ]; then
        echo "使用本地文件: $source_path"
        cp "$source_path" "$filename"
        
        if [ -f "$filename" ]; then
            echo "解压本地文件..."
            unzip -q "$filename" -d .
            # 重命名目录
            if [ -d "${dirname}-main" ]; then
                mv "${dirname}-main" "$dirname"
            elif [ -d "${dirname}-4.5.0" ]; then
                mv "${dirname}-4.5.0" "$dirname"
            elif [ -d "${dirname}-v4.5.0" ]; then
                mv "${dirname}-v4.5.0" "$dirname"
            fi
            rm "$filename"
            return 0
        fi
    else
        echo "本地文件 $source_path 不存在或为空"
        return 1
    fi
}

# 设置SDL2_image依赖库
cd "$SDL2_IMAGE_DIR"

# 清理现有文件
rm -rf jpeg png tiff webp

# 使用本地JPEG库
if [ ! -d "jpeg" ]; then
    if ! use_local_file "jpeg-main.zip" "jpeg"; then
        # 如果jpeg-main.zip不存在，尝试jpeg.zip
        use_local_file "jpeg.zip" "jpeg"
    fi
fi

# 使用本地PNG库
if [ ! -d "png" ]; then
    if ! use_local_file "lpng1650.zip" "png"; then
        # 如果lpng1650.zip不存在，尝试png.zip
        use_local_file "png.zip" "png"
    fi
fi

# 使用本地TIFF库
if [ ! -d "tiff" ]; then
    if ! use_local_file "tiff-4.5.0.zip" "tiff"; then
        # 如果tiff-4.5.0.zip不存在，尝试tiff.zip
        use_local_file "tiff.zip" "tiff"
    fi
fi

# 使用本地WEBP库
if [ ! -d "webp" ]; then
    if ! use_local_file "libwebp-main.zip" "webp"; then
        # 如果libwebp-main.zip不存在，尝试webp.zip
        use_local_file "webp.zip" "webp"
    fi
fi

# 返回项目目录
cd "$PROJECT_DIR"

# 检查所有依赖是否已设置
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
    echo "请手动检查 $SDL2_IMAGE_DIR 目录中的文件"
    exit 1
fi

# 返回项目目录
cd "$PROJECT_DIR"

# 开始构建APK
echo "开始构建APK..."
echo "完全使用本地资源以避免网络问题..."

buildozer android debug

if [ $? -eq 0 ]; then
    echo "APK构建成功完成！"
    echo "APK文件位置: $PROJECT_DIR/bin/"
else
    echo "构建失败，请检查错误日志"
    exit 1
fi