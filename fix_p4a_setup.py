#!/usr/bin/env python

import os
import sys
from pathlib import Path

def fix_p4a_setup():
    """
    修复 python-for-android 的 setup.py 文件，以确保与 buildozer 兼容
    """
    # 获取项目目录
    project_dir = Path(__file__).parent
    print(f"项目目录: {project_dir}")
    
    # 尝试多个可能的 python-for-android 目录位置
    possible_paths = [
        project_dir / ".buildozer" / "android" / "platform" / "python-for-android",
        Path("/mnt/d/python文件半成品/饮食规划/.buildozer/android/platform/python-for-android"),
        Path("/home/runner/.buildozer/android/platform/python-for-android"),
        project_dir / "python-for-android"
    ]
    
    p4a_dir = None
    for path in possible_paths:
        print(f"检查路径: {path}")
        if path.exists():
            p4a_dir = path
            print(f"找到 python-for-android 目录: {p4a_dir}")
            break
    
    if not p4a_dir:
        print("警告: 未找到 python-for-android 目录，将在项目根目录创建")
        p4a_dir = project_dir / "python-for-android"
        p4a_dir.mkdir(exist_ok=True)
    
    # 切换到 python-for-android 目录
    os.chdir(p4a_dir)
    print(f"当前工作目录: {os.getcwd()}")
    
    # 创建兼容 buildozer 解析的 setup.py 文件
    setup_content = '''#!/usr/bin/env python

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
'''
    
    # 写入 setup.py 文件
    with open('setup.py', 'w', encoding='utf-8') as f:
        f.write(setup_content)
    
    print("setup.py 文件已创建/更新")
    
    # 同时创建一个空的 __init__.py 文件确保这是一个有效的 Python 包
    init_file = p4a_dir / "pythonforandroid" / "__init__.py"
    init_file.parent.mkdir(exist_ok=True)
    init_file.touch()
    
    print("python-for-android 包结构已准备")
    return True

if __name__ == '__main__':
    try:
        if fix_p4a_setup():
            print("修复完成")
            sys.exit(0)
        else:
            print("修复失败")
            sys.exit(1)
    except Exception as e:
        print(f"修复过程中发生错误: {e}")
        sys.exit(1)