# 饮食规划应用APK构建指南

## 方法一：手动下载依赖进行本地构建

### 1. 下载必要组件

1. **下载python-for-android**:
   - 访问: https://github.com/kivy/python-for-android/archive/refs/heads/develop.zip
   - 将文件保存为 `python-for-android.zip`
   - 放置在项目根目录

2. **运行设置脚本**:
   ```bash
   cd /mnt/d/python文件半成品/饮食规划
   bash home/mrxh/projects/diet_planner/manual_p4a_setup.sh
   ```

3. **构建APK**:
   ```bash
   buildozer android debug
   ```

### 2. 系统依赖安装

确保安装了必要的系统依赖:

```bash
sudo apt update
sudo apt install -y build-essential libffi-dev libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev libncurses5-dev libncursesw5-dev liblzma-dev libxml2-dev libxslt1-dev libcurl4-openssl-dev libexpat1-dev
sudo apt install -y git wget libgl1 libglx-dev libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1
sudo apt install -y openjdk-17-jdk
```

## 方法二：使用GitHub Actions云端构建（推荐）

### 1. 推送代码到GitHub

1. 在GitHub上创建一个新的仓库
2. 将本地代码推送到该仓库

### 2. 触发构建

1. 推送代码后，GitHub Actions会自动开始构建
2. 或者在仓库页面手动触发工作流

### 3. 下载APK

1. 构建完成后，在Actions页面找到对应的运行记录
2. 在Artifacts部分下载生成的APK文件

## 方法三：使用Docker构建

### 1. 安装Docker

确保系统已安装Docker

### 2. 构建Docker镜像

```bash
# 创建Dockerfile（项目中已包含）
docker build -t dietplanner-builder .

# 运行构建
docker run --rm -v $(pwd):/app dietplanner-builder
```

## 常见问题解决

### 1. 网络问题（国内用户）

配置Git使用国内镜像:
```bash
git config --global url."https://ghproxy.com/https://github.com/".insteadOf "https://github.com/"
```

配置pip使用国内镜像:
```bash
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << 'EOF'
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple/
[install]
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF
```

### 2. SSL证书问题

```bash
git config --global http.sslVerify false
```

### 3. 权限问题

确保所有脚本具有执行权限:
```bash
chmod +x home/mrxh/projects/diet_planner/*.sh
```

## 构建时间说明

- **首次构建**: 20-40分钟（需要下载大量依赖）
- **后续构建**: 5-10分钟（利用缓存）
- **GitHub Actions**: 30-50分钟（每次都是全新环境）

## APK文件位置

构建成功后，APK文件位于:
- 本地构建: `bin/dietplanner-*-debug.apk`
- GitHub Actions: 工作流Artifacts中

如需进一步帮助，请查看相关文档或提交Issue。