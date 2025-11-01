#!/bin/bash

# 饮食规划应用 - GitHub推送问题解决方案

echo "饮食规划应用 - GitHub推送问题解决方案"
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

echo "1. 检查远程仓库配置..."
git remote -v

echo ""
echo "2. 清理代理配置..."
# 清除所有代理设置
git config --global --unset http.proxy 2>/dev/null
git config --global --unset https.proxy 2>/dev/null
git config --local --unset http.proxy 2>/dev/null
git config --local --unset https.proxy 2>/dev/null

echo ""
echo "3. 配置Git优化设置..."
# 使用HTTPS而非Git协议
git config --global url."https://".insteadOf git://

# 配置长期存储凭证
git config --global credential.helper store

# 增加Git缓冲区大小
git config --global http.postBuffer 1048576000

# 配置超时时间
git config --global http.lowSpeedLimit 0
git config --global http.lowSpeedTime 999999

echo ""
echo "4. 检查网络连接..."
# 获取Windows主机的IP地址
WINDOWS_HOST=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2; exit}')
echo "Windows主机IP: $WINDOWS_HOST"

echo ""
echo "5. 解决方案选项"

echo ""
echo "选项1: 使用个人访问令牌（推荐）"
echo "--------------------------------"
echo "1. 访问 https://github.com/settings/tokens"
echo "2. 点击 'Generate new token' 创建新令牌"
echo "3. 选择适当的权限（repo权限通常足够）"
echo "4. 复制生成的令牌"
echo "5. 运行以下命令使用令牌推送："
echo "   git push -u origin main"
echo "6. 当提示输入密码时，粘贴你的个人访问令牌"

echo ""
echo "选项2: 配置SSH密钥认证"
echo "----------------------"
echo "1. 生成SSH密钥（如果还没有）："
echo "   ssh-keygen -t ed25519 -C \"3084654305@qq.com\""
echo "2. 启动ssh-agent："
echo "   eval \"\$(ssh-agent -s)\""
echo "3. 添加SSH私钥到ssh-agent："
echo "   ssh-add ~/.ssh/id_ed25519"
echo "4. 复制公钥内容："
echo "   cat ~/.ssh/id_ed25519.pub"
echo "5. 将公钥添加到GitHub账户："
echo "   访问 https://github.com/settings/keys"
echo "   点击 'New SSH key' 并粘贴公钥"
echo "6. 更改远程URL为SSH方式："
echo "   git remote set-url origin git@github.com:2006dusk/2006dusk-diet-planner-app.git"
echo "7. 推送代码："
echo "   git push -u origin main"

echo ""
echo "选项3: 手动配置代理（如果在企业网络中）"
echo "--------------------------------------"
echo "如果需要配置代理，请根据你的网络环境运行以下命令之一："
echo "# 如果使用HTTP代理"
echo "git config --global http.proxy http://代理地址:端口"
echo "git config --global https.proxy https://代理地址:端口"
echo ""
echo "# 如果使用SOCKS代理"
echo "git config --global http.proxy socks5://代理地址:端口"
echo "git config --global https.proxy socks5://代理地址:端口"
echo ""
echo "# 取消代理配置"
echo "git config --global --unset http.proxy"
echo "git config --global --unset https.proxy"

echo ""
echo "6. 快速修复命令"
echo "----------------"
echo "尝试以下命令修复常见问题："
echo ""
echo "# 清理Git凭证缓存"
echo "echo '清除已存储的凭证...'"
echo "git config --global --unset credential.helper"
echo "git config --global credential.helper store"
echo ""
echo "# 重新尝试推送"
echo "git push -u origin main"

echo ""
echo "7. 调试命令"
echo "------------"
echo "如果问题仍然存在，可以使用以下命令调试："
echo ""
echo "# 测试网络连接"
echo "ping github.com"
echo ""
echo "# 测试HTTPS连接"
echo "curl -v https://github.com"
echo ""
echo "# 检查Git配置"
echo "git config --list | grep -E '(proxy|credential|url)'"
echo ""
echo "# 启用Git详细输出"
echo "GIT_TRACE=1 git push -u origin main"

echo ""
echo "请根据你的具体情况选择合适的解决方案。"
echo "推荐优先尝试选项1（个人访问令牌）。"