#!/bin/bash

# 手动下载并设置python-for-android

echo "开始手动下载并设置python-for-android..."

# 设置变量
PROJECT_DIR="/mnt/d/python文件半成品/饮食规划"
PLATFORM_DIR="$PROJECT_DIR/.buildozer/android/platform"
P4A_DIR="$PLATFORM_DIR/python-for-android"

# 创建必要的目录
mkdir -p "$PLATFORM_DIR"

# 检查是否已经存在python-for-android压缩包
if [ ! -f "$PROJECT_DIR/python-for-android.zip" ]; then
    echo "请手动下载python-for-android:"
    echo "1. 访问 https://github.com/kivy/python-for-android/archive/refs/heads/develop.zip"
    echo "2. 将下载的文件重命名为 python-for-android.zip"
    echo "3. 将文件放置在项目根目录中 (/mnt/d/python文件半成品/饮食规划/)"
    echo "4. 重新运行此脚本"
    echo ""
    echo "或者现在使用wget下载（需要网络连接）:"
    
    # 提示用户选择
    read -p "是否现在尝试下载? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "正在下载python-for-android..."
        wget -O "$PROJECT_DIR/python-for-android.zip" "https://github.com/kivy/python-for-android/archive/refs/heads/develop.zip"
        
        if [ $? -eq 0 ] && [ -f "$PROJECT_DIR/python-for-android.zip" ]; then
            echo "下载成功!"
        else
            echo "下载失败，请手动下载文件"
            exit 1
        fi
    else
        echo "请手动下载文件后重新运行此脚本"
        exit 1
    fi
fi

# 解压文件
echo "解压python-for-android..."
cd "$PLATFORM_DIR"
unzip -q "$PROJECT_DIR/python-for-android.zip"

# 重命名目录
mv python-for-android-develop python-for-android

# 进入目录并安装
cd "$P4A_DIR"
echo "安装python-for-android..."
pip3 install -e .

# 验证安装
echo "验证安装..."
python3 -c "import pythonforandroid; print('python-for-android安装成功')"

echo ""
echo "手动设置完成！"
echo "现在可以尝试运行构建命令:"
echo "buildozer android debug"
echo ""
echo "注意事项:"
echo "1. 首次构建会下载大量依赖，可能需要较长时间"
echo "2. 确保系统已安装必要的构建工具"
echo "3. 如果遇到SSL证书问题，可以配置Git忽略SSL验证:"
echo "   git config --global http.sslVerify false"