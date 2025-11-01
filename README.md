# 饮食规划应用

这是一个基于Kivy框架开发的Android饮食规划应用，可以帮助用户制定饮食计划、跟踪营养摄入、管理体重目标等。

## 功能特性

- 制定个性化饮食计划
- 跟踪每日营养摄入
- 管理体重目标
- 查看营养报告
- 浏览丰富食谱

## APK构建说明

由于buildozer在Windows上对Android构建支持有限，本项目提供三种构建方式：

### 方法一：使用Docker（推荐在Windows上使用）

项目包含了Docker配置文件，可以通过Docker容器构建APK，无需配置复杂的Linux环境。

1. 安装[Docker Desktop](https://www.docker.com/products/docker-desktop)
   - 下载并安装Docker Desktop
   - 启动Docker Desktop并等待其完全启动
   
2. 在项目根目录打开终端/命令提示符

3. 运行构建脚本：
   - Windows: 双击 `build_apk.bat` 或在命令行中运行 `build_apk.bat`
   - Linux/macOS: 在终端中运行 `chmod +x build_apk.sh && ./build_apk.sh`
   
4. 等待构建完成（首次构建会比较慢，因为需要下载基础镜像和依赖）

5. 生成的APK将在`bin`目录中

### 方法二：使用WSL (Windows Subsystem for Linux)

1. 安装WSL2：
   ```
   wsl --install
   ```

2. 重启电脑并完成WSL安装

3. 在WSL中安装必要依赖：
   ```bash
   sudo apt update
   sudo apt install -y build-essential libffi-dev zlib1g-dev liblzma-dev
   sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libc++-dev libc++abi-dev
   ```

4. 安装buildozer：
   ```bash
   pip3 install buildozer
   ```

5. 进入项目目录并构建APK：
   ```bash
   buildozer android debug
   ```

### 方法三：使用GitHub Actions (云端构建)

项目已配置GitHub Actions工作流，可自动构建APK：

1. 推送代码到仓库
2. GitHub Actions会自动构建APK
3. 在Actions页面下载构建好的APK

## 项目结构

```
饮食规划/
├── main.py                 # App入口和UI界面
├── nutrition.py            # 营养计算相关函数
├── recipe_core.py          # 食谱和餐单规划逻辑
├── buildozer.spec          # Android打包配置文件
├── requirements.txt        # Python依赖包
├── README.md               # 项目说明文档
├── kv_styles.kv            # 公共组件样式
├── components/             # 自定义组件
│   ├── custom_widgets.py   # 自定义UI组件
│   ├── charts.py           # 图表组件
├── modules/                # 功能模块
│   ├── home/               # 首页模块
│   │   └── home_screen.py  # 首页界面
│   ├── plan_diet/          # 饮食计划模块
│   │   ├── plan_screen.py  # 计划界面
│   │   ├── plan_generator.py # 计划生成器
│   │   └── advanced_food_selector.py # 高级食物选择器
│   ├── weight_plan/        # 体重规划模块
│   │   └── weight_screen.py # 体重规划界面
│   ├── recipes/            # 食谱管理模块
│   │   └── recipes_screen.py # 食谱管理界面
│   ├── report/             # 健康报告模块
│   │   └── report_screen.py # 健康报告界面
│   ├── body_data/          # 身体数据模块
│   │   └── body_data_screen.py # 身体数据界面
│   └── today_plan/         # 今日饮食计划模块
│       └── today_plan_screen.py # 今日饮食计划界面
├── utils/                  # 工具类
│   ├── nutrition_utils.py  # 营养计算工具
│   ├── data_manager.py     # 统一数据管理器（推荐使用）
│   └── user_profile.py     # 用户档案管理（已弃用，保留向后兼容）
├── fonts/                  # 字体文件目录
├── data/                   # 数据文件
│   ├── predefined_foods/   # 预定义食物数据
│   │   ├── fruits.json         # 水果数据
│   │   ├── staple_foods.json   # 主食数据
│   │   ├── prepared_dishes.json# 预制菜品数据
│   │   └── snacks.json         # 零食数据
│   └── user_data/          # 用户数据
│       └── user_data.json      # 统一用户数据文件（推荐使用）
└── transitions/            # 过渡动画
    └── smooth_slide.py     # 平滑滑动过渡
```

## 功能特性

1. 根据用户的体重、身高、年龄计算基础代谢率(BMR)
2. 计算每日总能量消耗(TDEE)
3. 根据热量需求计算宏量营养素分配(碳水化合物、蛋白质、脂肪)
4. 根据热量需求推荐每日餐单
5. 个性化饮食计划生成
6. 用户档案管理（体重记录、BMI计算）
7. 体重变化趋势图表展示
8. iOS风格的UI界面设计
9. 多维度健康数据追踪（体重、体脂率、三餐营养摄入）
10. 可视化数据图表展示
11. 自定义食物和食谱管理
12. 交互式饮食计划编辑

## 安装和运行

### 在桌面环境运行

1. 安装依赖:
   ```
   pip install -r requirements.txt
   ```

2. (可选) 下载推荐字体以获得更好的视觉效果:
   ```
   python download_font.py
   ```
   然后按照提示手动解压字体文件

3. 运行应用:
   ```
   python main.py
   ```

### 打包为Android APK

注意：打包过程需要在Linux或WSL环境下进行。

1. 安装必要依赖:
   ```
   sudo apt update && sudo apt install -y python3-pip openjdk-17-jdk git zip unzip
   pip install --user buildozer
   ```

2. 初始化Buildozer配置:
   ```
   cd 饮食规划
   buildozer init
   ```

3. 修改buildozer.spec中的关键配置项:
   ```
   requirements = python3,kivy
   android.permissions = INTERNET
   title = Diet Planner
   package.name = dietplanner
   package.domain = com.example
   ```

4. 编译APK (首次运行会下载NDK/SDK，大约1-2GB):
   ```
   buildozer android debug
   ```

5. 安装到设备:
   ```
   adb install -r bin/dietplanner-debug.apk
   ```

## 最近更新

1. 重构了项目结构，采用模块化设计
2. 优化了UI界面，提供更直观的操作体验
3. 增强了数据可视化功能，支持多种时间范围的图表展示
4. 改进了饮食计划生成算法，提供更个性化的建议
5. 添加了交互式饮食计划编辑功能，用户可以自定义餐食
6. 完善了用户档案管理功能，支持更全面的身体数据记录
7. 重命名了water_tracker模块为today_plan模块，更好地反映其显示今日饮食计划的功能
8. 实现了统一数据管理器，整合所有用户数据到单一文件中，提高数据一致性和管理效率
9. 弃用了旧的UserProfileManager，推荐使用统一的DataManager进行数据管理
10. 完成了从分散数据文件到统一user_data.json文件的完整迁移
11. 清理了冗余文件和目录，优化项目结构

## 可扩展方向

1. 添加账号系统 (Firebase Auth + Cloud Firestore)
2. 集成图像识别 (TensorFlow Lite估算食物重量)
3. AI餐单规划 (强化学习推荐)
4. 连接穿戴设备 (BLE读取运动数据)
5. 增加更多健康指标追踪（血压、血糖等）
6. 实现社交功能（分享饮食计划、健康成就）
7. 添加饮食记录拍照识别功能
8. 支持多语言界面

## 项目维护说明

为了保持项目的整洁和高效，建议定期清理以下内容：

1. 删除无用的缓存目录（如`__pycache__`、`.venv`、`.idea`等）
2. 删除未使用的图片文件（如`img.png`）
3. 删除空目录（如`docs/`）

项目中的以下文件和目录已经被移除：

- `utils/user_profile.py` - 已被`utils/data_manager.py`替代
- `data/user_profile.json` - 已被`data/user_data/user_data.json`替代
- `data/user_plan.json` - 已被整合到`data/user_data/user_data.json`中
- `data/history_plans.json` - 已被整合到`data/user_data/user_data.json`中

建议开发者使用`DataManager`类来管理所有用户数据，以确保数据一致性。