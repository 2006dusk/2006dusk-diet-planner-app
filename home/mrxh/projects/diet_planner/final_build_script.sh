#!/bin/bash

# 最终版饮食规划应用APK构建脚本 (WSL版本)
# 解决localhost代理和sudo密码问题

echo "开始配置饮食规划应用的APK构建环境..."

# 设置变量
PROJECT_DIR="/home/mrxh/projects/diet_planner"
BUILD_DIR="$PROJECT_DIR/.buildozer/android/platform"
P4A_DIR="$BUILD_DIR/python-for-android"

# 处理WSL代理问题
echo "处理WSL代理配置..."
# 获取Windows主机IP (通常为eth0接口的IP)
WIN_HOST=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2; exit;}')

# 如果存在代理配置，将其指向Windows主机而不是localhost
if env | grep -q "http_proxy\|https_proxy"; then
    echo "检测到代理配置，重新配置以适应WSL..."
    export http_proxy="http://${WIN_HOST}:$(echo $http_proxy | cut -d':' -f3)"
    export https_proxy="http://${WIN_HOST}:$(echo $https_proxy | cut -d':' -f3)"
    echo "新的代理设置: $http_proxy"
else
    echo "未检测到代理配置"
fi

# 进入项目目录
cd "$PROJECT_DIR"

# 验证Java安装
echo "验证Java环境..."
java -version

# 配置Git使用国内镜像源
echo "配置Git使用国内镜像源..."
git config --global url."https://ghproxy.com/https://github.com/".insteadOf "https://github.com/"
git config --global http.sslVerify false

# 预安装Cython (重要步骤，可以避免后续构建问题)
echo "安装Cython..."
pip3 install --upgrade Cython

# 清理之前的构建
echo "清理之前的构建..."
buildozer android clean

# 更新配置
echo "更新buildozer配置..."
sed -i 's/log_level =.*/log_level = 2/' buildozer.spec
sed -i 's/android.arch =.*/android.arch = arm64-v8a,armeabi-v7a/' buildozer.spec

# 添加p4a配置（如果不存在）
grep -q "p4a.no_git_clone" buildozer.spec || echo -e "\n# 禁止Git克隆以避免网络问题\np4a.no_git_clone = true" >> buildozer.spec

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
            unzip -q "$output" -d .
            # 重命名目录
            if [ -d "${dirname}-main" ]; then
                mv "${dirname}-main" "$dirname"
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
    download_with_retry "https://ghproxy.com/https://github.com/libsdl-org/tiff/archive/refs/heads/main.zip" "tiff.zip" "tiff"
fi

# 下载WEBP库
if [ ! -d "webp" ]; then
    download_with_retry "https://ghproxy.com/https://github.com/libsdl-org/webp/archive/refs/heads/main.zip" "webp.zip" "webp"
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