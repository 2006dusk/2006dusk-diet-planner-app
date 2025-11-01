# 字体文件目录

本目录应包含应用所需的字体文件，例如：

- Roboto-Regular.ttf
- Inter-Regular.ttf
- SanFrancisco-Regular.ttf

这些字体在 `main.py` 中被注册以支持中文显示.

## 推荐字体

为了获得更好的iOS风格UI体验，可以在此目录放置以下开源字体文件：

1. **Inter-Regular.ttf** - 与苹果San Francisco字体风格相似的开源字体
   - 下载地址：https://fonts.google.com/specimen/Inter
   
2. **Roboto-Regular.ttf** - Google设计的优秀字体
   - 下载地址：https://fonts.google.com/specimen/Roboto
   
3. **SanFrancisco-Regular.ttf** - Apple设计的系统字体（需要授权使用）
   - 说明：项目中已包含该字体文件
   
4. **OpenSans-Regular.ttf** - 广泛使用的开源字体
   - 下载地址：https://fonts.google.com/specimen/Open+Sans

## 使用说明

1. 从上述链接下载所需的字体文件
2. 将字体文件放置在此目录中
3. 应用会自动检测并使用项目目录中的字体文件
4. 如果没有找到项目字体，则会尝试使用系统字体
5. 如果系统字体也未找到，则会使用默认字体（可能无法正常显示中文）

## 注意事项

- 请确保下载的字体文件名与代码中指定的文件名一致
- 字体文件需要是.ttf或.otf格式
- 建议使用Inter字体以获得最接近iOS原生体验的效果
- 我们已添加了San Francisco的开源替代品(Inter字体)，以提供类似苹果系统的字体体验