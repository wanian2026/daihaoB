# 图标文件说明

## 当前状态
TradingBot.app 应用已创建，但缺少图标文件。

## 添加自定义图标

### 方法一：使用在线工具
1. 访问 https://www.iconfinder.com/ 或 https://www.flaticon.com/
2. 下载一个交易相关的图标（PNG格式，建议1024x1024像素）
3. 转换为 .icns 格式：
   - 访问: https://cloudconvert.com/png-to-icns
   - 上传PNG文件，转换为ICNS
   - 下载生成的 .icns 文件
4. 重命名为 `AppIcon.icns`
5. 放置到 `TradingBot.app/Contents/Resources/` 目录

### 方法二：使用命令行工具（推荐）
如果你有Homebrew，可以使用以下命令：

```bash
# 安装iconutil（macOS自带）或使用第三方工具
# 假设你有一个1024x1024的PNG图标文件：icon.png

# 创建图标集目录
mkdir -p icon.iconset

# 生成不同尺寸的图标
sips -z 16 16     icon.png --out icon.iconset/icon_16x16.png
sips -z 32 32     icon.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32     icon.png --out icon.iconset/icon_32x32.png
sips -z 64 64     icon.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128   icon.png --out icon.iconset/icon_128x128.png
sips -z 256 256   icon.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256   icon.png --out icon.iconset/icon_256x256.png
sips -z 512 512   icon.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512   icon.png --out icon.iconset/icon_512x512.png
sips -z 1024 1024 icon.png --out icon.iconset/icon_512x512@2x.png

# 生成.icns文件
iconutil -c icns icon.iconset -o AppIcon.icns

# 复制到应用包
cp AppIcon.icns TradingBot.app/Contents/Resources/
```

### 方法三：使用临时图标（快速测试）
如果你想快速测试应用，可以使用macOS内置的终端图标：

```bash
cp /System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/ExecutableBinaryIcon.icns TradingBot.app/Contents/Resources/AppIcon.icns
```

## 图标建议
- 建议使用与加密货币、交易、金融相关的图标
- 常见元素：比特币符号、股票图表、货币符号、机器人等
- 建议颜色：蓝色、绿色（代表金融）、橙色（代表加密货币）

## 验证图标
添加图标后，刷新Finder即可看到效果：
```bash
# 清除图标缓存
killall Dock

# 或使用Quick Look查看
qlmanage -p TradingBot.app
```
