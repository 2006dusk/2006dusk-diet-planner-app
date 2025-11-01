@echo off
echo 开始提交和推送代码更改...

echo 添加文件到暂存区...
git add .

echo 提交更改...
git commit -m "修复APK构建问题：同步依赖项、修复p4a配置、增强修复脚本"

echo 推送到远程仓库...
git push origin main

echo 代码提交和推送完成！
pause