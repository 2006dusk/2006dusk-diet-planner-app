#!/bin/bash

# 自动替换源并构建APK脚本
# 该脚本配置Git使用国内镜像源以解决网络连接问题

echo "开始配置国内镜像源并构建APK..."

# 设置项目路径
PROJECT_DIR="/home/mrxh/projects/diet_planner"
cd "$PROJECT_DIR"

# 配置Git使用国内镜像源
echo "配置Git使用国内镜像源..."
git config --global url."https://ghproxy.com/https://github.com/".insteadOf "https://github.com/"

# 配置http代理（如果需要）
# git config --global http.proxy http://127.0.0.1:1080
# git config --global https.proxy http://127.0.0.1:1080

# 更新buildozer.spec配置文件，添加no_git_clone选项
echo "更新buildozer.spec配置..."
if ! grep -q "p4a.no_git_clone = true" buildozer.spec; then
    echo "" >> buildozer.spec
    echo "# 使用本地p4a，避免Git克隆问题" >> buildozer.spec
    echo "p4a.no_git_clone = true" >> buildozer.spec
fi

# 清理之前的构建
echo "清理之前的构建..."
buildozer android clean

# 创建SDL2_image外部依赖目录
SDL2_IMAGE_DIR="$PROJECT_DIR/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/bootstrap_builds/sdl2/jni/SDL2_image/external"
mkdir -p "$SDL2_IMAGE_DIR"

# 定义带重试功能的下载函数
download_with_retry() {
    local url=$1
    local output=$2
    local dirname=$3
    local max_retries=3
    local retry_count=0
    
    echo "下载 $dirname..."
    
    while [ $retry_count -lt $max_retries ]; do
        echo "尝试下载 $url (第 $((retry_count+1)) 次)..."
        wget --timeout=30 --tries=1 "$url" -O "$output"
        
        if [ $? -eq 0 ] && [ -f "$output" ]; then
            echo "下载成功: $output"
            # 解压文件
            unzip -q "$output"
            mv "${dirname}-main" "$dirname"
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

# 下载JPEG库
if [ ! -d "jpeg" ]; then
    download_with_retry "https://ghproxy.com/https://github.com/libsdl-org/jpeg/archive/refs/heads/main.zip" "jpeg.zip" "jpeg-main"
fi

# 下载PNG库
if [ ! -d "png" ]; then
    download_with_retry "https://ghproxy.com/https://github.com/libsdl-org/png/archive/refs/heads/main.zip" "png.zip" "png-main"
fi

# 下载TIFF库
if [ ! -d "tiff" ]; then
    download_with_retry "https://ghproxy.com/https://github.com/libsdl-org/tiff/archive/refs/heads/main.zip" "tiff.zip" "tiff-main"
fi

# 下载WEBP库
if [ ! -d "webp" ]; then
    download_with_retry "https://ghproxy.com/https://github.com/libsdl-org/webp/archive/refs/heads/main.zip" "webp.zip" "webp-main"
fi

# 返回项目目录
cd "$PROJECT_DIR"

# 开始构建APK
echo "开始构建APK..."
echo "使用国内镜像源以提高下载速度..."

MAX_RETRIES=1
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