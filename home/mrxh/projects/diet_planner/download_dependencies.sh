#!/bin/bash

# 下载和解压SDL2_image依赖库的可靠脚本

PROJECT_DIR="/mnt/d/python文件半成品/饮食规划/home/mrxh/projects/diet_planner"
SDL2_IMAGE_DIR="$PROJECT_DIR/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/bootstrap_builds/sdl2/jni/SDL2_image/external"

# 创建目标目录
mkdir -p "$SDL2_IMAGE_DIR"
cd "$SDL2_IMAGE_DIR"

# 定义带重试功能和验证的下载函数
download_and_extract() {
    local url=$1
    local output_name=$2
    local target_dir=$3
    local max_retries=3
    local retry_count=0
    
    echo "下载 $target_dir..."
    
    while [ $retry_count -lt $max_retries ]; do
        echo "尝试下载 $url (第 $((retry_count+1)) 次)..."
        
        # 下载文件
        wget --timeout=60 --tries=1 "$url" -O "${output_name}.zip"
        
        # 检查下载是否成功
        if [ $? -eq 0 ] && [ -f "${output_name}.zip" ]; then
            # 检查文件是否为有效的zip文件
            if unzip -t "${output_name}.zip" >/dev/null 2>&1; then
                echo "下载成功: ${output_name}.zip"
                
                # 解压文件
                unzip -q "${output_name}.zip"
                
                # 检查解压后的目录结构
                if [ -d "${output_name}-main" ]; then
                    mv "${output_name}-main" "$target_dir"
                    echo "成功解压并重命名 $target_dir"
                elif [ -d "$output_name" ]; then
                    echo "目录已存在，使用原名称"
                else
                    echo "警告: 无法找到解压后的目录"
                fi
                
                # 清理zip文件
                rm "${output_name}.zip"
                return 0
            else
                echo "下载的文件不是有效的zip文件"
            fi
        else
            echo "下载失败"
        fi
        
        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $max_retries ]; then
            echo "等待5秒后重试..."
            sleep 5
        fi
    done
    
    echo "下载 $target_dir 失败，已达到最大重试次数"
    return 1
}

# 下载JPEG库
if [ ! -d "jpeg" ]; then
    download_and_extract "https://ghproxy.com/https://github.com/libsdl-org/jpeg/archive/refs/heads/main.zip" "jpeg" "jpeg"
fi

# 下载PNG库
if [ ! -d "png" ]; then
    download_and_extract "https://ghproxy.com/https://github.com/libsdl-org/png/archive/refs/heads/main.zip" "png" "png"
fi

# 下载TIFF库
if [ ! -d "tiff" ]; then
    download_and_extract "https://ghproxy.com/https://github.com/libsdl-org/tiff/archive/refs/heads/main.zip" "tiff" "tiff"
fi

# 下载WEBP库
if [ ! -d "webp" ]; then
    download_and_extract "https://ghproxy.com/https://github.com/libsdl-org/webp/archive/refs/heads/main.zip" "webp" "webp"
fi

echo "所有依赖库下载完成"