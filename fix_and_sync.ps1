#!/usr/bin/env powershell
# fix_and_sync.ps1 - 自动化修复和同步脚本

# 作者: Lingma
# 日期: 2025-10-31
# 功能: 修复Buildozer构建问题并同步Git仓库

# 检查是否在项目根目录
$projectRoot = "D:\python文件半成品\饮食规划"
Set-Location $projectRoot

Write-Host "正在检查项目配置..."

# 1. 检查并修复buildozer.spec配置
$specFile = "$projectRoot\buildozer.spec"
if (Test-Path $specFile) {
    $content = Get-Content $specFile -Raw
    if (-not ($content -match 'p4a.source_dir = .')) {
        Write-Host "添加p4a.source_dir配置..."
        $content += "
p4a.source_dir = ."
    }
    if (-not ($content -match 'p4a.no_git_clone = true')) {
        Write-Host "添加p4a.no_git_clone配置..."
        $content += "
p4a.no_git_clone = true"
    }
    Set-Content $specFile $content
}

# 2. 安装必要的Android构建工具
Write-Host "正在安装Android构建工具..."

# 检查Android SDK是否已安装
$androidSdkPath = "C:\Users\$env:USERNAME\AppData\Local\Android\Sdk"
if (-not (Test-Path $androidSdkPath)) {
    Write-Host "Android SDK未找到，正在下载...
    # 这里需要手动下载Android SDK或使用其他方法
    # 由于权限限制，我们无法自动下载
    Write-Host "请手动下载Android SDK并安装到默认位置"
}

# 3. 更新Buildozer和p4a
Write-Host "正在更新Buildozer和p4a..."
try {
    python -m pip install --upgrade buildozer python-for-android
} catch {
    Write-Host "更新失败，请确保Python和pip已正确安装"
}

# 4. 配置Git
Write-Host "正在配置Git..."
try {
    git config --global --unset http.proxy
    git config --global --unset https.proxy
    git config --global url."https://".insteadOf git://
    git config --global http.postBuffer 1048576000
    git config --global http.lowSpeedLimit 0
    git config --global http.lowSpeedTime 999999
} catch {
    Write-Host "Git配置失败，请检查Git是否已安装"
}

# 5. 同步Git仓库
Write-Host "正在同步Git仓库..."
try {
    # 检查工作区状态
    git status
    
    # 添加所有更改
    git add .
    
    # 提交更改
    $commitMessage = "Automated fix and sync on $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    git commit -m $commitMessage
    
    # 推送到远程仓库
    git push origin main
    
    Write-Host "Git同步成功！"
} catch {
    Write-Host "Git同步失败，错误信息：$($_.Exception.Message)"
    Write-Host "建议使用GitHub Web界面手动上传代码"
}

Write-Host "脚本执行完成！"
