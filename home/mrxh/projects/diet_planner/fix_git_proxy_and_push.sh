#!/bin/bash

# 脚本功能：修复WSL中的Git代理配置并推送代码到GitHub

echo "修复WSL中的Git代理配置并推送代码到GitHub"
echo "========================================"

# 检查当前目录
echo "当前工作目录: $(pwd)"

# 检查是否在正确的项目目录中
if [[ ! -f "main.py" ]]; then
    echo "警告: 未在项目根目录中，正在切换目录..."
    cd /mnt/d/python文件半成品/饮食规划 2>/dev/null || cd /home/mrxh/projects/diet_planner 2>/dev/null
    echo "已切换到: $(pwd)"
fi

# 检查是否存在Git仓库
if [[ ! -d ".git" ]]; then
    echo "错误: 当前目录不是Git仓库"
    exit 1
fi

# 检查远程仓库配置
echo "检查远程仓库配置..."
git remote -v

# 修复代理配置
echo "修复代理配置..."
# 取消所有代理设置
git config --global --unset http.proxy
git config --global --unset https.proxy
git config --local --unset http.proxy
git config --local --unset https.proxy

# 配置WSL特定的网络设置
echo "配置WSL网络设置..."

# 获取Windows主机的IP地址（通常为WSL的网关）
WINDOWS_HOST=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2; exit}')
echo "Windows主机IP: $WINDOWS_HOST"

# 如果有代理设置，尝试配置为Windows主机的代理
if [[ ! -z "$WINDOWS_HOST" ]]; then
    echo "尝试配置代理到Windows主机..."
    # 这里可以根据需要配置特定的代理端口
    # git config --global http.proxy http://$WINDOWS_HOST:端口号
    # git config --global https.proxy https://$WINDOWS_HOST:端口号
fi

# 使用HTTPS而非Git协议
git config --global url."https://".insteadOf git://

# 配置长期存储凭证
git config --global credential.helper store

# 尝试增加Git缓冲区大小
git config --global http.postBuffer 1048576000

# 尝试推送代码
echo "尝试推送代码到GitHub..."
echo "如果提示输入用户名和密码，请使用GitHub个人访问令牌而不是密码"

# 尝试推送
git push -u origin main

if [ $? -eq 0 ]; then
    echo "成功推送代码到GitHub!"
else
    echo "推送失败，尝试使用SSH方式..."
    echo "请确保你已经在GitHub上配置了SSH密钥"
    
    # 配置SSH方式的远程仓库（如果尚未配置）
    CURRENT_URL=$(git remote get-url origin)
    if [[ $CURRENT_URL == https* ]]; then
        SSH_URL=${CURRENT_URL/https:\/\/github.com\//git@github.com:}
        echo "SSH URL: $SSH_URL"
        # 注意：这里不自动更改远程URL，只显示SSH URL供用户手动更改
        echo "如需使用SSH，请手动运行:"
        echo "git remote set-url origin $SSH_URL"
    fi
fi

echo "脚本执行完成"
echo "如果仍有问题，请检查:"
echo "1. 网络连接"
echo "2. 防火墙设置"
echo "3. 是否需要配置代理"
echo "4. GitHub凭据配置"