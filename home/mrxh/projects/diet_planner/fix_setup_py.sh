#!/bin/bash

# 修复setup.py文件以兼容buildozer解析

echo "修复setup.py文件以兼容buildozer解析"
echo "=================================="

# 设置变量
PROJECT_DIR="/mnt/d/python文件半成品/饮食规划"
P4A_DIR="$PROJECT_DIR/.buildozer/android/platform/python-for-android"

# 进入python-for-android目录
cd "$P4A_DIR"

# 创建兼容buildozer解析的setup.py文件
cat > setup.py << 'EOF'
#!/usr/bin/env python

from setuptools import setup, find_packages

# Normal installation dependencies
# 这个变量名和格式是buildozer所期望的
install_reqs = [
    'appdirs',
    'colorama>=0.3.3',
    'jinja2',
    'six',
    'enum34; python_version<"3.4"',
    'sh>=1.10; sys_platform!="nt"',
    'pep517',
    'toml',
    'packaging',
]

setup(
    name='python-for-android',
    version='0.1',
    description='Python for android',
    author='Kivy Team',
    author_email='kivy-dev@googlegroups.com',
    url='https://github.com/kivy/python-for-android',
    license='MIT',
    install_requires=install_reqs,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'python-for-android = pythonforandroid.entrypoints:main',
            'p4a = pythonforandroid.entrypoints:main',
        ],
    },
)
EOF

# 重新安装python-for-android
pip3 install -e . --quiet

echo "setup.py文件已修复并重新安装"
echo "现在可以尝试运行构建命令:"
echo "buildozer android debug"