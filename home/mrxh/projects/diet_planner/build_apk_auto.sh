#!/bin/bash

# 饮食规划应用APK自动化构建脚本
# 该脚本处理常见构建问题并自动重试

echo "开始配置饮食规划应用的APK构建环境..."

# 设置项目路径
PROJECT_DIR="/home/mrxh/projects/diet_planner"
BUILD_DIR="$PROJECT_DIR/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a"
SDL2_IMAGE_DIR="$BUILD_DIR/build/bootstrap_builds/sdl2/jni/SDL2_image/external"

# 检查项目目录
if [ ! -d "$PROJECT_DIR" ]; then
    echo "错误: 项目目录不存在: $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR"

# 更新系统证书
echo "更新系统证书..."
sudo apt update
sudo apt install -y ca-certificates

# 安装Cython（如果尚未安装）
echo "检查并安装Cython..."
pip3 install cython --user

# 配置Git SSL设置
echo "配置Git SSL设置..."
git config --global http.sslBackend openssl

# 清理之前的构建
echo "清理之前的构建..."
buildozer android clean

# 检查并创建SDL2_image外部依赖目录
echo "检查并创建SDL2_image外部依赖目录..."
mkdir -p "$SDL2_IMAGE_DIR"

# 尝试手动下载SDL2_image依赖（如果自动下载失败）
cd "$SDL2_IMAGE_DIR"
if [ ! -d "jpeg" ] || [ ! -d "png" ]; then
    echo "手动下载SDL2_image依赖库..."
    
    # 下载JPEG库
    if [ ! -d "jpeg" ]; then
        echo "下载JPEG库..."
        wget https://github.com/libsdl-org/jpeg/archive/refs/heads/main.zip -O jpeg.zip
        if [ -f "jpeg.zip" ]; then
            unzip jpeg.zip
            mv jpeg-main jpeg
            rm jpeg.zip
        fi
    fi
    
    # 下载PNG库
    if [ ! -d "png" ]; then
        echo "下载PNG库..."
        wget https://github.com/libsdl-org/png/archive/refs/heads/main.zip -O png.zip
        if [ -f "png.zip" ]; then
            unzip png.zip
            mv png-main png
            rm png.zip
        fi
    fi
    
    # 下载TIFF库
    if [ ! -d "tiff" ]; then
        echo "下载TIFF库..."
        wget https://github.com/libsdl-org/tiff/archive/refs/heads/main.zip -O tiff.zip
        if [ -f "tiff.zip" ]; then
            unzip tiff.zip
            mv tiff-main tiff
            rm tiff.zip
        fi
    fi
    
    # 下载WEBP库
    if [ ! -d "webp" ]; then
        echo "下载WEBP库..."
        wget https://github.com/libsdl-org/webp/archive/refs/heads/main.zip -O webp.zip
        if [ -f "webp.zip" ]; then
            unzip webp.zip
            mv webp-main webp
            rm webp.zip
        fi
    fi
fi

# 返回项目目录
cd "$PROJECT_DIR"

# 检查buildozer.spec配置
echo "检查buildozer.spec配置..."
if ! grep -q "p4a.no_git_clone = true" buildozer.spec; then
    echo "更新buildozer.spec配置..."
    echo "" >> buildozer.spec
    echo "# 自动化构建配置" >> buildozer.spec
    echo "p4a.no_git_clone = true" >> buildozer.spec
fi

# 开始构建APK
echo "开始构建APK..."
echo "如果遇到网络问题，脚本将尝试自动重试..."

MAX_RETRIES=3
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "尝试构建 #$RETRY_COUNT..."
    
    ~/.local/bin/buildozer android debug
    
    if [ $? -eq 0 ]; then
        echo "APK构建成功完成！"
        echo "APK文件位置: $PROJECT_DIR/bin/"
        exit 0
    else
        echo "构建失败，错误代码: $?"
        if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
            echo "等待10秒后重试..."
            sleep 10
        fi
    fi
done

echo "构建失败，已达到最大重试次数 ($MAX_RETRIES)"
echo "请检查错误日志并手动解决问题"
exit 1