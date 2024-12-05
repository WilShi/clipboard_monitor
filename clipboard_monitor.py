import tkinter as tk
from tkinter import messagebox, colorchooser, font
import pyperclip
import psutil
import os
import json
from datetime import datetime
import logging

class ClipboardMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Clipboard Monitor")
        self.clipboard_text = ""
        self.clipboard_history = {}
        
        # 获取脚本所在目录并构建历史记录文件路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.history_file = os.path.join(script_dir, "clipboard_history.json")
        self.log_file = os.path.join(script_dir, "clipboard_monitor.log")
        self.config_file = os.path.join(script_dir, "config.json")

        # 配置日志记录
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 加载历史记录
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as file:
                try:
                    data = json.load(file)
                    if isinstance(data, dict):
                        self.clipboard_history = data
                    else:
                        logging.warning("History file format is incorrect. Converting to dictionary.")
                        self.clipboard_history = {datetime.now().isoformat(): entry for entry in data}
                except json.JSONDecodeError:
                    logging.error("Failed to decode JSON from history file. Creating a new empty history.")
                    self.clipboard_history = {}

        # 加载配置
        self.load_config()
        

        # 创建框架用于显示剪切板内容和历史记录
        self.frame = tk.Frame(root, bg=self.bg_color)
        self.frame.pack(padx=10, pady=10)
        
        # 创建文本框用于显示当前剪切板内容
        self.current_clipboard_label = tk.Label(self.frame, text="Current Clipboard:", font=(self.lable_font, self.lable_font_size, self.lable_font_weight), bg=self.bg_color, fg="white")
        self.current_clipboard_label.grid(row=0, column=0, sticky="w")
        self.text_box = tk.Text(self.frame, wrap=tk.WORD, height=5, width=40, state=tk.DISABLED, font=(self.content_font, self.content_font_size, self.content_font_weight))
        self.text_box.grid(row=1, column=0, padx=10, pady=10)

        # 创建标签用于显示CPU和内存使用情况
        self.status_label = tk.Label(root, text="", font=(self.lable_font, self.lable_font_size, self.lable_font_weight), bg=self.bg_color, fg="white")
        self.status_label.pack(pady=5)

        # 创建列表框用于显示剪切板历史记录
        self.history_listbox = tk.Listbox(root, height=10, width=40, font=(self.content_font, self.content_font_size, self.content_font_weight), selectmode=tk.SINGLE)
        self.history_listbox.pack(padx=10, pady=10)
        self.update_history_listbox()

        # 绑定双击事件以复制选中的历史记录
        self.history_listbox.bind('<Double-Button-1>', self.copy_selected_record)

        # 启动第一次检查
        self.check_clipboard()

        # 设置窗口始终在最顶层
        self.topmost_var = tk.BooleanVar(value=True)
        self.topmost_checkbox = tk.Checkbutton(root, text="Keep window on top", variable=self.topmost_var, command=self.toggle_topmost)
        
        # 管理历史记录的按钮
        self.manage_history_button = tk.Button(root, text="Manage History", command=self.open_history_window)
        
        # 清空所有记录的按钮
        self.clear_all_button = tk.Button(root, text="Clear All", command=self.clear_all_records)
        
        # 使用 pack 布局管理器将复选框和按钮放在同一行
        frame = tk.Frame(root)
        frame.pack(pady=5, expand=True, fill=tk.X)
        
        self.topmost_checkbox.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.manage_history_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.clear_all_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # 初始设置
        self.toggle_topmost()
        
        self.history_window = None

        # 设置窗口透明度和背景色
        self.root.attributes("-alpha", self.alpha)
        self.root.configure(bg=self.bg_color)

        # 启动第一次日志清理检查
        self.check_and_clean_log_file()

        # 创建菜单栏
        self.create_menu()



    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # 透明度菜单
        transparency_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Transparency", menu=transparency_menu)
        for alpha in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
            label_text = f"{int(alpha * 100)}%"
            if alpha == self.alpha:
                # 高亮显示当前的 alpha 值
                transparency_menu.add_command(label=label_text, command=lambda a=alpha: self.set_alpha(a), font=("Arial", 11, "bold"), background="lightblue")
            else:
                transparency_menu.add_command(label=label_text, command=lambda a=alpha: self.set_alpha(a), font=("Arial", 11, "normal"))

        # 颜色菜单
        color_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Color", menu=color_menu)
        color_menu.add_command(label="Choose Background Color", command=self.choose_bg_color)

        # 字体菜单
        font_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Font", menu=font_menu)

        # 字体选择子菜单
        # 标签子菜单
        font_name_menu = tk.Menu(font_menu, tearoff=0)
        font_menu.add_cascade(label="Font Name - Label", menu=font_name_menu)
        available_fonts = list(font.families())
        for font_name in available_fonts:
            if font_name == self.lable_font:
                # 高亮显示当前的字体名称
                font_name_menu.add_command(label=font_name, command=lambda fn=font_name: self.set_font_name(fn, "label"), font=(font_name, 11, "bold"), background="lightblue")
            else:
                font_name_menu.add_command(label=font_name, command=lambda fn=font_name: self.set_font_name(fn, "label"), font=(font_name, 11, "normal"))

        # 内容子菜单
        font_name_menu_content = tk.Menu(font_menu, tearoff=0)
        font_menu.add_cascade(label="Font Name - Content", menu=font_name_menu_content)
        for font_name in available_fonts:
            if font_name == self.content_font:
                # 高亮显示当前的字体名称
                font_name_menu_content.add_command(label=font_name, command=lambda fn=font_name: self.set_font_name(fn, "content"), font=(font_name, 11, "bold"), background="lightblue")
            else:
                font_name_menu_content.add_command(label=font_name, command=lambda fn=font_name: self.set_font_name(fn, "content"), font=(font_name, 11, "normal"))
                
        # 字体大小子菜单
        # 标签子菜单
        font_size_menu = tk.Menu(font_menu, tearoff=0)
        font_menu.add_cascade(label="Font Size - Label", menu=font_size_menu)
        for font_size in [8, 9, 10, 11, 12, 13, 14, 16, 18, 20, 22, 24, 26, 28, 36, 48, 72]:
            if font_size == self.lable_font_size:
                # 高亮显示当前的字体大小
                font_size_menu.add_command(label=str(font_size), command=lambda fs=font_size: self.set_font_size(fs, "label"), font=("Arial", 11, "bold"), background="lightblue")
            else:
                font_size_menu.add_command(label=str(font_size), command=lambda fs=font_size: self.set_font_size(fs, "label"), font=("Arial", 11, "normal"))

        # 内容子菜单
        font_size_menu_content = tk.Menu(font_menu, tearoff=0)
        font_menu.add_cascade(label="Font Size - Content", menu=font_size_menu_content)
        for font_size in [8, 9, 10, 11, 12, 13, 14, 16, 18, 20, 22, 24, 26, 28, 36, 48, 72]:
            if font_size == self.content_font_size:
                # 高亮显示当前的字体大小
                font_size_menu_content.add_command(label=str(font_size), command=lambda fs=font_size: self.set_font_size(fs, "content"), font=("Arial", 11, "bold"), background="lightblue")
            else:
                font_size_menu_content.add_command(label=str(font_size), command=lambda fs=font_size: self.set_font_size(fs, "content"), font=("Arial", 11, "normal"))
        


        # # 字体颜色子菜单
        # font_color_menu = tk.Menu(font_menu, tearoff=0)
        # font_menu.add_cascade(label="Font Color - Label", menu=font_color_menu)
        # font_color_menu.add_command(label="Choose Font Color", command=self.choose_font_color)

        # 字体粗细子菜单
        # 标签子菜单
        font_weight_menu = tk.Menu(font_menu, tearoff=0)
        font_menu.add_cascade(label="Font Weight - Label", menu=font_weight_menu)
        for font_weight in ["normal", "bold"]:
            if font_weight == self.lable_font_weight:
                # 高亮显示当前的字体粗细
                font_weight_menu.add_command(label=font_weight, command=lambda fw=font_weight: self.set_font_weight(fw, "label"), font=("Arial", 11, "bold"), background="lightblue")
            else:
                font_weight_menu.add_command(label=font_weight, command=lambda fw=font_weight: self.set_font_weight(fw, "label"), font=("Arial", 11, "normal"))

        # 内容子菜单
        font_weight_menu_content = tk.Menu(font_menu, tearoff=0)
        font_menu.add_cascade(label="Font Weight - Content", menu=font_weight_menu_content)
        for font_weight in ["normal", "bold"]:
            if font_weight == self.content_font_weight:
                # 高亮显示当前的字体粗细
                font_weight_menu_content.add_command(label=font_weight, command=lambda fw=font_weight: self.set_font_weight(fw, "content"), font=("Arial", 11, "bold"), background="lightblue")
            else:
                font_weight_menu_content.add_command(label=font_weight, command=lambda fw=font_weight: self.set_font_weight(fw, "content"), font=("Arial", 11, "normal"))
    


    def set_alpha(self, alpha):
        self.alpha = alpha
        self.root.attributes("-alpha", self.alpha)
        self.save_config()
        self.create_menu()
        logging.info(f"Transparency set to {alpha * 100}%")

    def choose_bg_color(self):
        color_code = colorchooser.askcolor(title="Choose Background Color")[1]
        if color_code:
            self.bg_color = color_code
            self.root.configure(bg=self.bg_color)
            self.frame.configure(bg=self.bg_color)
            self.current_clipboard_label.configure(bg=self.bg_color)
            self.status_label.configure(bg=self.bg_color)
            self.save_config()
            logging.info(f"Background color set to {color_code}")


    def set_font_name(self, font_name, text_type):
        if text_type == "label":
            self.lable_font = font_name
            self.current_clipboard_label.configure(font=(self.lable_font, self.lable_font_size, self.lable_font_weight))
            self.status_label.configure(font=(self.lable_font, self.lable_font_size, self.lable_font_weight))
        else:
            self.content_font = font_name
            self.text_box.configure(font=(self.content_font, self.content_font_size, self.content_font_weight))
            self.history_listbox.configure(font=(self.content_font, self.content_font_size, self.content_font_weight))

        self.save_config()
        self.create_menu()
        logging.info(f"Font name {text_type} set to {font_name}")

    def set_font_size(self, font_size, text_type):
        if text_type == "label":
            self.lable_font_size = font_size
            self.current_clipboard_label.configure(font=(self.lable_font, self.lable_font_size, self.lable_font_weight))
            self.status_label.configure(font=(self.lable_font, self.lable_font_size, self.lable_font_weight))
        else:
            self.content_font_size = font_size
            self.text_box.configure(font=(self.content_font, self.content_font_size, self.content_font_weight))
            self.history_listbox.configure(font=(self.content_font, self.content_font_size, self.content_font_weight))

        self.save_config()
        self.create_menu()
        logging.info(f"Font size {text_type} set to {font_size}")


    def choose_font_color(self):
        color_code = colorchooser.askcolor(title="Choose Font Color")[1]
        if color_code:
            self.root.option_add("*Foreground", color_code)

    def set_font_weight(self, weight, text_type):
        if text_type == "label":
            self.lable_font_weight = weight
            self.current_clipboard_label.configure(font=(self.lable_font, self.lable_font_size, self.lable_font_weight))
            self.status_label.configure(font=(self.lable_font, self.lable_font_size, self.lable_font_weight))
        else:
            self.content_font_weight = weight
            self.text_box.configure(font=(self.content_font, self.content_font_size, self.content_font_weight))
            self.history_listbox.configure(font=(self.content_font, self.content_font_size, self.content_font_weight))

        self.save_config()
        self.create_menu()
        logging.info(f"Font weight {text_type} set to {weight}")



    def load_config(self):
        default_config = {
            "alpha": 0.7, 
            "bg_color": "#333333",
            "lable_font": "Arial",
            "lable_font_size": 11,
            "lable_font_weight": "normal",
            "content_font": "Arial",
            "content_font_size": 11,
            "content_font_weight": "normal"
            }
        

        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as file:
                try:
                    config = json.load(file)
                    self.alpha = config.get("alpha", default_config["alpha"])
                    self.bg_color = config.get("bg_color", default_config["bg_color"])
                    # 加载字体配置项
                    self.lable_font = config.get("lable_font", default_config["lable_font"])
                    self.lable_font_size = config.get("lable_font_size", default_config["lable_font_size"])
                    self.lable_font_weight = config.get("lable_font_weight", default_config["lable_font_weight"])
                    self.content_font = config.get("content_font", default_config["content_font"])
                    self.content_font_size = config.get("content_font_size", default_config["content_font_size"])
                    self.content_font_weight = config.get("content_font_weight", default_config["content_font_weight"])
                    logging.info("Loaded configuration from file.")

                except json.JSONDecodeError:
                    logging.error("Failed to decode JSON from config file. Using default configuration.")
                    self.alpha = default_config["alpha"]
                    self.bg_color = default_config["bg_color"]
                    # 使用默认字体配置项
                    self.lable_font = default_config["lable_font"]
                    self.lable_font_size = default_config["lable_font_size"]
                    self.lable_font_weight = default_config["lable_font_weight"]
                    self.content_font = default_config["content_font"]
                    self.content_font_size = default_config["content_font_size"]
                    self.content_font_weight = default_config["content_font_weight"]
                    logging.info("Using default configuration.")
                    self.save_config()

        else:
            logging.info("Configuration file not found. Using default configuration.")
            self.alpha = default_config["alpha"]
            self.bg_color = default_config["bg_color"]
            self.lable_font = default_config["lable_font"]
            self.lable_font_size = default_config["lable_font_size"]
            self.lable_font_weight = default_config["lable_font_weight"]
            self.content_font = default_config["content_font"]
            self.content_font_size = default_config["content_font_size"]
            self.content_font_weight = default_config["content_font_weight"]
            self.save_config()


    def save_config(self):
        config = {
            "alpha": self.alpha, 
            "bg_color": self.bg_color, 
            "lable_font": self.lable_font,
            "lable_font_size": self.lable_font_size,
            "lable_font_weight": self.lable_font_weight,
            "content_font": self.content_font,
            "content_font_size": self.content_font_size,
            "content_font_weight": self.content_font_weight
            }
        
        try:
            with open(self.config_file, 'w') as file:
                json.dump(config, file, indent=4)
            logging.info("Saved configuration to file.")
        except Exception as e:
            logging.error(f"Failed to save configuration to file: {e}")



    def toggle_topmost(self):
        self.root.attributes("-topmost", self.topmost_var.get())

    
    def clear_all_records(self):
        # 弹出确认对话框
        result = messagebox.askyesno("Clear All Records", "Are you sure you want to clear all clipboard records?")
        if result:
            # 清空历史记录
            self.clipboard_history.clear()
            # 更新历史记录显示
            self.update_history_listbox()
            self.save_history_to_file()
            messagebox.showinfo("Clear All Records", "All clipboard records have been cleared.")
            logging.info("All clipboard records have been cleared.")



    def open_history_window(self):
        if self.history_window:
            return

        logging.info("Opening history window")

        self.history_window = tk.Toplevel(self.root)
        self.history_window.title("Clipboard History")
        self.history_window.protocol("WM_DELETE_WINDOW", self.close_history_window)

        # 设置窗口的初始大小，例如宽度为 800 像素，高度为 600 像素
        self.history_window.geometry("800x600")

        # 将窗口置顶
        self.history_window.wm_attributes("-topmost", 1)

        self.history_listbox_inner = tk.Listbox(self.history_window, selectmode=tk.MULTIPLE)
        self.history_listbox_inner.pack(fill=tk.BOTH, expand=True)

        # 按时间戳倒序排序
        sorted_timestamps = sorted(self.clipboard_history.keys(), reverse=True)

        for index, timestamp in enumerate(sorted_timestamps):
            content = self.clipboard_history[timestamp]
            self.history_listbox_inner.insert(tk.END, f"{timestamp}: {content}")

        # 设置交替行的颜色
        for i in range(0, self.history_listbox_inner.size()):
            bg_color = 'white' if i % 2 == 0 else '#E8E8E8'
            self.history_listbox_inner.itemconfig(i, bg=bg_color)

        delete_button = tk.Button(self.history_window, text="Delete Selected", command=self.delete_selected)
        delete_button.pack(pady=5)

        save_button = tk.Button(self.history_window, text="Save and Close", command=self.save_and_close)
        save_button.pack(pady=5)



    def close_history_window(self):
        self.history_window.destroy()
        self.history_window = None

    def delete_selected(self):
        selected_indices = self.history_listbox_inner.curselection()
        # print(selected_indices)

        if not selected_indices:
            messagebox.showwarning("No Selection", "Please select one or more items to delete.")
            return

        # 获取所有时间戳的列表
        timestamps = sorted(self.clipboard_history.keys(), reverse=True)
        # print(timestamps)

        # 使用 reversed 遍历选定的索引，以避免在删除过程中索引变化导致的问题
        for index in reversed(selected_indices):
            if index < len(timestamps):
                timestamp = timestamps[index]
                logging.info(f"Deleting item with timestamp: {timestamp}")  # 调试信息
                del self.clipboard_history[timestamp]
            else:
                logging.error(f"Index {index} out of range")

        # print(self.clipboard_history)

        # 清空 Listbox 并重新插入剩余的历史记录
        self.history_listbox_inner.delete(0, tk.END)
        for timestamp in sorted(self.clipboard_history.keys(), reverse=True):
            content = self.clipboard_history[timestamp]
            self.history_listbox_inner.insert(tk.END, f"{timestamp}: {content[:50]}")
            logging.info(f"Reinserting item with timestamp: {timestamp}, content: {content[:50]}")  # 调试信息



    def save_and_close(self):
        # 保存历史记录到文件，并更新显示
        self.update_history_listbox()
        self.save_history_to_file()
        self.close_history_window()
        logging.info("History saved and window closed")


    def check_clipboard(self):
        try:
            new_clipboard_text = pyperclip.paste()
            if new_clipboard_text != self.clipboard_text:
                if not self.check_worng_clipboard(new_clipboard_text):
                    self.clipboard_text = new_clipboard_text
                    self.update_text_box(new_clipboard_text)
                    self.add_to_history(new_clipboard_text)
        except pyperclip.PyperclipException as pe:
            logging.error(f"Pyperclip error: {pe}")
        except Exception as e:
            logging.error(f"Error accessing clipboard: {e}")
        
        self.root.after(500, self.check_clipboard)

    def check_worng_clipboard(self, text):
        worng = ['••••••••••']
        if text in worng:
            logging.warning(f"Clipboard contains worng text: {text}")
            pyperclip.copy(self.clipboard_text)
            logging.warning(f"Clipboard has been replaced with the original text: {self.clipboard_text[:50]}")
            return True
        return False


    def update_text_box(self, text):
        # 允许编辑以更新内容
        self.text_box.config(state=tk.NORMAL)
        self.text_box.delete('1.0', tk.END)
        self.text_box.insert(tk.END, text)
        # 更新完成后再次设为不可编辑
        self.text_box.config(state=tk.DISABLED)

    def add_to_history(self, text):
        logging.info(f"Adding to clipboard history: {text[:50]}")  # 调试信息
        timestamp = datetime.now().isoformat()
        self.clipboard_history[timestamp] = text
        self.update_history_listbox()
        # 只有当历史记录发生变化时才写入文件
        self.save_history_to_file()

    def save_history_to_file(self):
        try:
            with open(self.history_file, 'w') as file:
                json.dump(self.clipboard_history, file, indent=4)
            logging.info("Saved clipboard history to file.")
        except Exception as e:
            logging.error(f"Failed to save clipboard history to file: {e}")

    def update_history_listbox(self):
        self.history_listbox.delete(0, tk.END)

        for timestamp in sorted(self.clipboard_history.keys(), reverse=True):
            record = self.clipboard_history[timestamp][:50]  # 显示前50个字符
            self.history_listbox.insert(tk.END, f"{record}")

        for i in range(0, self.history_listbox.size()):
            bg_color = 'white' if i % 2 == 0 else '#E8E8E8'
            self.history_listbox.itemconfig(i, bg=bg_color)

    def copy_selected_record(self, event):
        selected_index = self.history_listbox.curselection()
        if selected_index:
            selected_timestamp = sorted(self.clipboard_history.keys(), reverse=True)[selected_index[0]]
            selected_record = self.clipboard_history[selected_timestamp]
            pyperclip.copy(selected_record)
            self.update_text_box(selected_record)
            self.clipboard_text = selected_record
            logging.info(f"Copied selected record to clipboard: {selected_record[:50]}")

    def update_system_info(self):
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_usage = psutil.virtual_memory().percent
            self.status_label.config(text=f"CPU Usage: {cpu_usage}% | Memory Usage: {memory_usage}%")
            # logging.info(f"System Info - CPU Usage: {cpu_usage}%, Memory Usage: {memory_usage}%")
        except psutil.Error as pe:
            logging.error(f"Psutil error: {pe}")
        except Exception as e:
            logging.error(f"Failed to get system info: {e}")
        self.root.after(1000, self.update_system_info)  # 每秒更新一次系统信息

    def check_and_clean_log_file(self):
        set_max_log_size = 2  # 5 MB
        if os.path.exists(self.log_file):
            log_size = os.path.getsize(self.log_file)
            max_log_size = set_max_log_size * 1024 * 1024
            if log_size > max_log_size:
                with open(self.log_file, 'w') as file:
                    file.truncate(0)  # 清空文件
                logging.info(f"Log file size exceeds {set_max_log_size}MB. Clearing the log file.")
        # 每隔十分钟检查一次日志文件
        self.root.after(600000, self.check_and_clean_log_file)

if __name__ == "__main__":
    root = tk.Tk()
    app = ClipboardMonitor(root)
    app.update_system_info()  # 初始化系统信息更新
    root.mainloop()



