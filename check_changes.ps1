# 检查项目文件更改状态的 PowerShell 脚本

Write-Host "检查饮食规划项目的文件更改状态..." -ForegroundColor Green

# 获取最近一小时内修改的文件
Write-Host "`n最近修改的文件:" -ForegroundColor Yellow
Get-ChildItem -Recurse | Where-Object {!$_.PSIsContainer -and $_.LastWriteTime -gt (Get-Date).AddHours(-1)} | 
    Select-Object FullName, LastWriteTime | 
    Sort-Object LastWriteTime -Descending |
    Format-Table -AutoSize

# 显示具体的更改文件内容
Write-Host "`n本次会话修改的文件:" -ForegroundColor Yellow
$recentFiles = Get-ChildItem -Recurse | Where-Object {!$_.PSIsContainer -and $_.LastWriteTime -gt (Get-Date).AddHours(-1)} | 
    Sort-Object LastWriteTime -Descending

foreach ($file in $recentFiles) {
    Write-Host "`n文件: $($file.FullName)" -ForegroundColor Cyan
    try {
        $content = Get-Content $file.FullName -First 5
        Write-Host "前5行内容:"
        $content | Write-Host
    } catch {
        Write-Host "无法读取文件内容" -ForegroundColor Red
    }
}

Write-Host "`n如需使用 Git 进行版本控制，请执行以下操作:" -ForegroundColor Green
Write-Host "1. 安装 Git for Windows (https://git-scm.com/download/win)" -ForegroundColor Gray
Write-Host "2. 打开 Git Bash 或 PowerShell" -ForegroundColor Gray
Write-Host "3. 运行以下命令:" -ForegroundColor Gray
Write-Host "   git add ." -ForegroundColor Gray
Write-Host "   git commit -m '描述您的更改'" -ForegroundColor Gray
Write-Host "   git push origin main" -ForegroundColor Gray