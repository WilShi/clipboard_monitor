# Clipboard Monitor

## 简介
Clipboard Monitor 是一个用 Python 编写的剪切板监控工具。它可以实时监控剪切板内容的变化，并将其记录在历史记录中。此外，它还提供了多种自定义选项，如窗口透明度、背景颜色、字体样式等。

## 功能
- 实时监控剪切板内容
- 记录剪切板历史
- 自定义窗口透明度、背景颜色、字体样式
- 查看和管理剪切板历史记录
- 显示系统 CPU 和内存使用情况
- 日志记录和清理

## 安装
### 环境要求
- Python 3.6 或更高版本
- Tkinter 库
- Pyperclip 库
- Psutil 库

### 安装步骤
1. **安装 Python**:
   如果你还没有安装 Python，请访问 [Python 官方网站](https://www.python.org/) 下载并安装最新版本。

2. **安装依赖库**:
   打开终端或命令提示符，运行以下命令安装所需的库：
   ```sh
   pip install pyperclip psutil
   ```

3. **克隆项目**:
   从 GitHub 或其他源代码仓库克隆项目到本地：
   ```sh
   git clone https://github.com/WilShi/clipboard_monitor.git
   cd clipboard_monitor
   ```

## 使用方法
1. **运行程序**:
   在项目根目录下运行以下命令启动程序：
   ```sh
   python clipboard_monitor.py
   ```

2. **界面说明**:
   - **当前剪切板内容**: 显示当前剪切板中的内容。
   - **历史记录列表**: 显示剪切板的历史记录。
   - **系统信息**: 显示当前系统的 CPU 和内存使用情况。
   - **保持窗口置顶**: 选择是否将窗口始终保持在最顶层。
   - **管理历史记录**: 打开历史记录管理窗口，可以删除选定的历史记录。
   - **清空所有记录**: 清空所有剪切板历史记录。

3. **自定义选项**:
   - **透明度**: 通过菜单栏的 "Transparency" 选项调整窗口透明度。
   - **背景颜色**: 通过菜单栏的 "Color" 选项选择背景颜色。
   - **字体样式**: 通过菜单栏的 "Font" 选项调整标签和内容的字体名称、大小和粗细。

## 配置
程序会读取和写入以下配置文件：
- `config.json`: 存储用户自定义的透明度、背景颜色、字体样式等配置。
- `clipboard_history.json`: 存储剪切板历史记录。
- `clipboard_monitor.log`: 存储程序的日志信息。

### 默认配置
```json
{
    "alpha": 0.7,
    "bg_color": "#333333",
    "lable_font": "Arial",
    "lable_font_size": 11,
    "lable_font_weight": "normal",
    "content_font": "Arial",
    "content_font_size": 11,
    "content_font_weight": "normal"
}
```

## 常见问题
### 1. 程序无法启动
- **解决方法**:
  - 确保已安装所有依赖库。
  - 检查 Python 版本是否符合要求。
  - 运行程序时查看终端输出的错误信息，根据错误信息进行排查。

### 2. 剪切板内容未更新
- **解决方法**:
  - 确保剪切板中有新的内容。
  - 检查程序是否有权限访问剪切板。

### 3. 日志文件过大
- **解决方法**:
  - 程序会自动每十分钟检查一次日志文件大小，超过 2MB 时会清空日志文件。
  - 你也可以手动删除 `clipboard_monitor.log` 文件。

## 贡献
欢迎贡献代码和提出改进建议！请遵循以下步骤：
1. Fork 项目。
2. 创建一个新的分支。
3. 提交你的更改。
4. 提交 Pull Request。

## 许可证
本项目采用 MIT 许可证，详情参见 [LICENSE](LICENSE) 文件。

## 联系
如果有任何问题或建议，请联系 [1638083992@qq.com](mailto:1638083992@qq.com)。
```
