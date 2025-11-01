#!/bin/bash

# 完整的GitHub SSH配置和推送脚本

echo "开始配置GitHub SSH连接和推送代码"

# 切换到项目目录
cd /mnt/d/python文件半成品/饮食规划 || cd /home/mrxh/projects/diet_planner

echo "当前目录: $(pwd)"

# 确保SSH agent正在运行
echo "启动ssh-agent..."
eval "$(ssh-agent -s)"

# 添加SSH密钥
echo "添加SSH密钥..."
ssh-add ~/.ssh/id_ed25519

# 验证SSH连接
echo "验证SSH连接到GitHub..."
ssh -T git@github.com

# 设置Git用户信息（如果没有配置的话）
echo "配置Git用户信息..."
git config --global user.email "3084654305@qq.com"
git config --global user.name "2006dusk"

# 确保使用SSH URL
echo "设置远程仓库URL为SSH方式..."
git remote set-url origin git@github.com:2006dusk/2006dusk-diet-planner-app.git

# 显示当前远程配置
echo "当前远程仓库配置:"
git remote -v

# 获取当前分支名称
BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)
echo "当前分支: $BRANCH_NAME"

# 尝试推送代码
echo "尝试推送代码到GitHub..."
git push -u origin $BRANCH_NAME

echo "脚本执行完成。"
echo "如果推送成功，你的代码现在已经同步到GitHub仓库。"
echo "如果还有问题，请检查："
echo "1. SSH密钥是否正确添加到GitHub账户"
echo "2. 网络连接是否正常"
echo "3. 是否有防火墙或代理阻止连接"