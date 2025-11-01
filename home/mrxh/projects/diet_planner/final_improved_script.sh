#!/bin/bash

# 最终改进版饮食规划应用APK构建脚本 (WSL版本)
# 解决SSL连接和本地资源利用问题

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

# 进入项目目录 (使用WSL原生路径)
if [ ! -d "$PROJECT_DIR" ]; then
    echo "创建项目目录: $PROJECT_DIR"
    mkdir -p "$PROJECT_DIR"
fi

echo "复制项目文件到WSL原生路径..."
rsync -av --exclude='.git' --exclude='*.pyc' --exclude='__pycache__' /mnt/d/python文件半成品/饮食规划/ "$PROJECT_DIR/"

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
# 先清除可能存在的冲突配置
git config --global --unset url."https://ghproxy.com/https://github.com/".insteadOf 2>/dev/null || true

# 使用清华大学镜像源（更稳定）
git config --global url."https://mirrors.tuna.tsinghua.edu.cn/git/".insteadOf "https://github.com/"

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

# 定义带重试功能的下载函数（使用多种镜像源）
download_with_retry() {
    local url=$1
    local output=$2
    local dirname=$3
    local max_retries=3
    local retry_count=0
    
    echo "下载 $dirname..."
    
    # 首先检查本地是否已存在对应的zip文件
    LOCAL_ZIP="/mnt/d/python文件半成品/饮食规划/${dirname}.zip"
    if [ -f "$LOCAL_ZIP" ] && [ -s "$LOCAL_ZIP" ]; then
        echo "使用本地文件: $LOCAL_ZIP"
        cp "$LOCAL_ZIP" "$output"
        
        if [ -f "$output" ]; then
            echo "解压本地文件..."
            unzip -q "$output" -d .
            # 重命名目录
            if [ -d "${dirname}-main" ]; then
                mv "${dirname}-main" "$dirname"
            elif [ -d "${dirname}-4.5.0" ]; then
                mv "${dirname}-4.5.0" "$dirname"
            elif [ -d "${dirname}-v4.5.0" ]; then
                mv "${dirname}-v4.5.0" "$dirname"
            fi
            rm "$output"
            return 0
        fi
    fi
    
    # 尝试不同的镜像源
    local urls=(
        "https://mirrors.tuna.tsinghua.edu.cn/github-release/libsdl-org/$dirname/refs/heads/main.zip"
        "https://ghproxy.com/https://github.com/libsdl-org/$dirname/archive/refs/heads/main.zip"
        "https://github.com/libsdl-org/$dirname/archive/refs/heads/main.zip"
    )
    
    while [ $retry_count -lt $max_retries ]; do
        for mirror_url in "${urls[@]}"; do
            echo "尝试下载 $mirror_url (第 $((retry_count+1)) 次)..."
            wget --timeout=30 --tries=1 "$mirror_url" -O "$output"
            
            if [ $? -eq 0 ] && [ -f "$output" ]; then
                echo "下载成功: $output"
                # 解压文件
                unzip -q "$output" -d .
                # 重命名目录
                if [ -d "${dirname}-main" ]; then
                    mv "${dirname}-main" "$dirname"
                elif [ -d "${dirname}-4.5.0" ]; then
                    mv "${dirname}-4.5.0" "$dirname"
                elif [ -d "${dirname}-v4.5.0" ]; then
                    mv "${dirname}-v4.5.0" "$dirname"
                fi
                rm "$output"
                return 0
            else
                echo "从 $mirror_url 下载失败"
            fi
        done
        
        echo "所有镜像源都下载失败，等待5秒后重试..."
        retry_count=$((retry_count + 1))
        sleep 5
    done
    
    echo "下载 $dirname 失败，已达到最大重试次数"
    return 1
}

# 手动下载SDL2_image依赖库
cd "$SDL2_IMAGE_DIR"

# 清理现有文件（但保留本地已有的zip文件）
rm -rf jpeg png tiff webp

# 下载JPEG库
if [ ! -d "jpeg" ]; then
    download_with_retry "jpeg" "jpeg.zip" "jpeg"
fi

# 下载PNG库
if [ ! -d "png" ]; then
    download_with_retry "png" "png.zip" "png"
fi

# 下载TIFF库 (使用特定版本)
if [ ! -d "tiff" ]; then
    # 首先尝试使用本地文件
    LOCAL_TIFF="/mnt/d/python文件半成品/饮食规划/tiff-4.5.0.zip"
    if [ -f "$LOCAL_TIFF" ] && [ -s "$LOCAL_TIFF" ]; then
        echo "使用本地TIFF文件..."
        cp "$LOCAL_TIFF" "tiff.zip"
        unzip -q "tiff.zip" -d .
        mv "tiff-4.5.0" "tiff"
        rm "tiff.zip"
    else
        # 尝试从镜像下载
        echo "下载TIFF库..."
        local urls=(
            "https://mirrors.tuna.tsinghua.edu.cn/github-release/libsdl-org/tiff/refs/tags/v4.5.0.zip"
            "https://ghproxy.com/https://github.com/libsdl-org/tiff/archive/refs/tags/v4.5.0.zip"
            "https://github.com/libsdl-org/tiff/archive/refs/tags/v4.5.0.zip"
        )
        
        local downloaded=false
        for mirror_url in "${urls[@]}"; do
            echo "尝试下载 $mirror_url..."
            wget --timeout=30 --tries=1 "$mirror_url" -O "tiff.zip"
            
            if [ $? -eq 0 ] && [ -f "tiff.zip" ]; then
                echo "下载成功: tiff.zip"
                unzip -q "tiff.zip" -d .
                mv "tiff-4.5.0" "tiff"
                rm "tiff.zip"
                downloaded=true
                break
            else
                echo "从 $mirror_url 下载失败"
            fi
        done
        
        if [ "$downloaded" = false ]; then
            echo "TIFF库下载失败"
        fi
    fi
fi

# 下载WEBP库
if [ ! -d "webp" ]; then
    download_with_retry "webp" "webp.zip" "webp"
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
    echo "请手动检查 $SDL2_IMAGE_DIR 目录中的文件"
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
    
    # 将APK复制回Windows路径
    echo "将APK复制回Windows路径..."
    mkdir -p /mnt/d/python文件半成品/饮食规划/bin
    cp bin/*.apk /mnt/d/python文件半成品/饮食规划/bin/
    echo "APK已复制到: /mnt/d/python文件半成品/饮食规划/bin/"
else
    echo "构建失败，请检查错误日志"
    exit 1
fi