#!/bin/bash

# 设置python-for-android目录的脚本

echo "设置python-for-android目录..."

# 设置变量
PROJECT_DIR="/mnt/d/python文件半成品/饮食规划"
P4A_DIR="$PROJECT_DIR/.buildozer/android/platform/python-for-android"

# 进入项目目录
cd "$PROJECT_DIR"

# 确保目录存在
mkdir -p "$P4A_DIR"
cd "$P4A_DIR"

# 初始化Git仓库（如果需要）
if [ ! -d ".git" ]; then
    echo "初始化Git仓库..."
    git init
    git config user.email "mrxh@example.com"
    git config user.name "mrxh"
fi

# 添加远程仓库
git remote remove origin 2>/dev/null
git remote add origin https://github.com/kivy/python-for-android.git

# 创建基本文件结构
echo "创建基本文件结构..."

# 创建setup.py文件
cat > setup.py << 'EOF'
#!/usr/bin/env python

from setuptools import setup

setup(
    name='python-for-android',
    version='0.1',
    description='Python for android',
    author='Kivy Team',
    author_email='kivy-dev@googlegroups.com',
    url='https://github.com/kivy/python-for-android',
    packages=['pythonforandroid'],
)
EOF

# 创建基本的pythonforandroid目录结构
mkdir -p pythonforandroid

# 创建__init__.py文件
cat > pythonforandroid/__init__.py << 'EOF'
__version__ = '0.1'
EOF

# 创建一个基本的__main__.py文件
cat > pythonforandroid/__main__.py << 'EOF'
if __name__ == '__main__':
    print("Python for Android")
EOF

# 如果有初始提交，添加这些文件
if git log --oneline -1 >/dev/null 2>&1; then
    git add .
    git commit -m "Add basic python-for-android structure"
else
    # 创建初始提交
    git add .
    git commit -m "Initial commit with basic python-for-android structure"
fi

# 确保在master分支上
git checkout -b master 2>/dev/null || git checkout master

echo "python-for-android目录设置完成!"
echo "现在可以尝试运行构建命令:"
echo "buildozer android debug"