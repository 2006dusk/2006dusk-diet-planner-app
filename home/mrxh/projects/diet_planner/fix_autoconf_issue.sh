#!/bin/bash

# 修复 autoconf 参数错误问题的脚本

echo "开始修复 autoconf 参数错误问题..."

# 检查 autoconf 版本
echo "检查 autoconf 安装情况..."
if command -v autoconf >/dev/null 2>&1; then
    AUTOCONF_VERSION=$(autoconf --version | head -n1)
    echo "已安装: $AUTOCONF_VERSION"
else
    echo "未找到 autoconf，正在安装..."
    sudo apt update
    sudo apt install -y autoconf automake build-essential
fi

# 检查 autoreconf 是否可用
echo "检查 autoreconf..."
if command -v autoreconf >/dev/null 2>&1; then
    AUTORECONF_VERSION=$(autoreconf --version | head -n1)
    echo "已安装: $AUTORECONF_VERSION"
else
    echo "安装 autoreconf..."
    sudo apt install -y dh-autoreconf
fi

# 设置项目路径
PROJECT_DIR="/mnt/d/python文件半成品/饮食规划"
P4A_DIR="$PROJECT_DIR/.buildozer/android/platform/python-for-android"

# 检查是否存在 python-for-android 目录
if [ ! -d "$P4A_DIR" ]; then
    echo "警告: 未找到 python-for-android 目录"
    echo "请先运行初始化脚本再执行此修复"
    exit 1
fi

# 进入 python-for-android 目录
cd "$P4A_DIR"

# 查找可能存在问题的 configure.ac 或 configure.in 文件
echo "检查 configure.ac 或 configure.in 文件..."
CONFIGURE_FILES=$(find . -name "configure.ac" -o -name "configure.in" | head -5)

if [ -n "$CONFIGURE_FILES" ]; then
    echo "找到配置文件:"
    echo "$CONFIGURE_FILES"
    
    # 对每个找到的配置文件运行 autoreconf
    for CONFIG_FILE in $CONFIGURE_FILES; do
        DIR_PATH=$(dirname "$CONFIG_FILE")
        echo "在目录 $DIR_PATH 运行 autoreconf..."
        cd "$DIR_PATH"
        autoreconf -fiv 2>/dev/null || echo "警告: 在 $DIR_PATH 运行 autoreconf 失败"
        cd "$P4A_DIR"
    done
else
    echo "未找到 configure.ac 或 configure.in 文件"
fi

# 检查并修复可能的参数冲突
TOOLCHAIN_DIR="$P4A_DIR/pythonforandroid/toolchain"
if [ -d "$TOOLCHAIN_DIR" ]; then
    echo "检查 toolchain 配置..."
    
    # 确保 main.py 文件存在
    if [ -f "$TOOLCHAIN_DIR/main.py" ]; then
        # 检查是否有 argparse 相关的参数定义冲突
        if grep -q "add_argument.*-h.*--help" "$TOOLCHAIN_DIR/main.py"; then
            echo "发现可能的参数冲突，应用修复..."
            
            # 应用修复，移除重复的 -h/--help 定义
            sed -i 's/parser\.add_argument.*-h.*--help.*//' "$TOOLCHAIN_DIR/main.py"
            echo "已修复 toolchain 中的参数冲突"
        fi
    fi
fi

echo ""
echo "autoconf 问题修复完成！"
echo ""
echo "建议执行以下步骤继续构建："
echo "1. 清理之前的构建:"
echo "   buildozer android clean"
echo ""
echo "2. 重新构建应用:"
echo "   buildozer android debug"
echo ""
echo "如果仍有问题，请尝试更新所有依赖:"
echo "   pip install --upgrade Cython buildozer python-for-android"