#!/bin/bash

# 修复构建目录和项目属性文件问题

echo "修复构建目录和项目属性文件问题..."

# 设置变量
PROJECT_DIR="/mnt/d/python文件半成品/饮食规划"
BUILD_DIR="$PROJECT_DIR/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a"
DIST_DIR="$BUILD_DIR/dists/dietplanner"

# 创建必要的目录结构
mkdir -p "$DIST_DIR"

# 创建project.properties文件
cat > "$DIST_DIR/project.properties" << 'EOF'
# Project target.
target=android-33
EOF

# 创建其他可能需要的文件
# 创建local.properties文件
cat > "$DIST_DIR/local.properties" << 'EOF'
# Local Properties
sdk.dir=/home/mrxh/.buildozer/android/platform/android-sdk
ndk.dir=/home/mrxh/.buildozer/android/platform/android-ndk-r25b
EOF

# 创建build.gradle文件（简化版本）
cat > "$DIST_DIR/build.gradle" << 'EOF'
buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:7.0.0'
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}
EOF

# 创建settings.gradle文件
cat > "$DIST_DIR/settings.gradle" << 'EOF'
rootProject.name = 'dietplanner'
EOF

# 创建一个基本的AndroidManifest.xml文件
mkdir -p "$DIST_DIR/src/main"
cat > "$DIST_DIR/src/main/AndroidManifest.xml" << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.dietplanner"
    android:versionCode="1"
    android:versionName="0.1">

    <uses-sdk android:minSdkVersion="21" android:targetSdkVersion="33" />

    <application
        android:label="饮食规划"
        android:icon="@drawable/icon"
        android:theme="@android:style/Theme.DeviceDefault">
        <activity
            android:name="org.kivy.android.PythonActivity"
            android:exported="true"
            android:configChanges="orientation|keyboardHidden|screenSize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

</manifest>
EOF

echo "构建目录和必要文件创建完成!"
echo "现在可以尝试运行构建命令:"
echo "buildozer android debug"