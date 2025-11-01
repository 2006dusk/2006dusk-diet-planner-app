# Git 提交和推送脚本

Write-Host "开始提交和推送代码更改..." -ForegroundColor Green

# 设置 Git 的路径（根据您的实际安装路径调整）
$gitPath = "C:\Program Files\Git\bin\git.exe"

# 如果找不到 git.exe，则尝试使用系统 PATH 中的 git
if (!(Test-Path $gitPath)) {
    Write-Host "未找到 Git 可执行文件，尝试使用系统 PATH 中的 git..." -ForegroundColor Yellow
    $gitPath = "git"
}

try {
    # 添加所有更改到暂存区
    Write-Host "添加文件到暂存区..." -ForegroundColor Cyan
    & $gitPath add .
    
    # 提交更改
    Write-Host "提交更改..." -ForegroundColor Cyan
    & $gitPath commit -m "修复APK构建问题：同步依赖项、修复p4a配置、增强修复脚本"
    
    # 推送到远程仓库
    Write-Host "推送到远程仓库..." -ForegroundColor Cyan
    & $gitPath push origin main
    
    Write-Host "代码提交和推送完成！" -ForegroundColor Green
}
catch {
    Write-Host "执行 Git 命令时出错: $_" -ForegroundColor Red
    Write-Host "请确保 Git 已正确安装并添加到系统 PATH 中" -ForegroundColor Yellow
}