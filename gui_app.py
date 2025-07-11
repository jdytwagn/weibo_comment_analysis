import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from weibo_spider import extract_mid_from_url, get_weibo_id_from_mid, get_all_comments
from sentiment_analysis import analyze_sentiment_with_hybrid as analyze_sentiment
from visualization import generate_wordcloud, plot_sentiment_distribution
import os
import json
import threading
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime


class WeiboAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("微博评论情感分析系统")
        self.root.geometry("1200x800")
        self.root.configure(bg="#2c3e50")

        self.current_user = None
        self.users_file = "users.json"
        self.config_file = "config.json"
        self.load_users()
        self.config = self.load_config()

        self.bg_image = None
        self.bg_label = None

        self.create_login_screen()

        self.wordcloud_img = None
        self.sentiment_img = None

    def load_users(self):
        try:
            with open(self.users_file, 'r') as f:
                self.users = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.users = {}

    def save_users(self):
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f)

    def load_config(self):
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_config(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f)

    def get_user_background_path(self):
        if self.current_user and "user_backgrounds" in self.config:
            return self.config["user_backgrounds"].get(self.current_user)
        return None

    def set_background(self, image_path=None):
        if self.bg_label:
            self.bg_label.destroy()

        if image_path:
            try:
                bg_image = Image.open(image_path)
                bg_image = bg_image.resize((self.root.winfo_width(), self.root.winfo_height()), Image.LANCZOS)
                self.bg_image = ImageTk.PhotoImage(bg_image)
                self.bg_label = tk.Label(self.root, image=self.bg_image)
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                self.bg_label.lower()

                if self.current_user:
                    self.config.setdefault("user_backgrounds", {})
                    self.config["user_backgrounds"][self.current_user] = image_path
                    self.save_config()
            except Exception as e:
                messagebox.showwarning("警告", f"背景图片加载失败，使用默认背景: {str(e)}")
                self.set_background(None)
        else:
            self.bg_label = tk.Label(self.root, bg="#2c3e50")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            if self.current_user and "user_backgrounds" in self.config:
                self.config["user_backgrounds"].pop(self.current_user, None)
                self.save_config()

    def create_login_screen(self):
        self.clear_window()
        self.set_background(self.get_user_background_path())

        title_label = tk.Label(self.root, text="微博评论情感分析系统", font=("Microsoft YaHei", 28, "bold"), fg="white",
                               bg="#2c3e50")
        title_label.pack(pady=50)

        login_frame = tk.Frame(self.root, bg="#34495e", bd=2, relief="ridge", padx=20, pady=20)
        login_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(login_frame, text="用户登录", font=("Microsoft YaHei", 16), bg="#34495e", fg="#3498db").pack(pady=10)

        tk.Label(login_frame, text="用户名:", font=("Microsoft YaHei", 12), bg="#34495e", fg="white").pack(anchor="w",
                                                                                                        pady=5)
        self.username_entry = tk.Entry(login_frame, font=("Microsoft YaHei", 12), bg="#2c3e50", fg="white")
        self.username_entry.pack(fill="x", pady=5)

        tk.Label(login_frame, text="密码:", font=("Microsoft YaHei", 12), bg="#34495e", fg="white").pack(anchor="w",
                                                                                                       pady=5)
        self.password_entry = tk.Entry(login_frame, show="*", font=("Microsoft YaHei", 12), bg="#2c3e50", fg="white")
        self.password_entry.pack(fill="x", pady=5)

        btn_frame = tk.Frame(login_frame, bg="#34495e")
        btn_frame.pack(fill="x", pady=10)

        tk.Button(btn_frame, text="登录", command=self.login, font=("Microsoft YaHei", 12), bg="#3498db", fg="white",
                  relief="flat", padx=15).pack(side="left", padx=10)
        tk.Button(btn_frame, text="注册", command=self.show_register, font=("Microsoft YaHei", 12), bg="#2ecc71",
                  fg="white", relief="flat", padx=15).pack(side="left", padx=10)

        tk.Button(self.root, text="设置背景", command=self.choose_background, font=("Microsoft YaHei", 10), bg="#34495e",
                  fg="white", relief="flat").place(relx=0.95, rely=0.05, anchor="ne")

    def show_register(self):
        register_window = tk.Toplevel(self.root)
        register_window.title("用户注册")
        register_window.geometry("400x400")
        register_window.configure(bg="#2c3e50")
        register_window.transient(self.root)
        register_window.grab_set()

        tk.Label(register_window, text="用户注册", font=("Microsoft YaHei", 16), bg="#2c3e50", fg="#3498db").pack(pady=10)

        tk.Label(register_window, text="用户名:", font=("Microsoft YaHei", 12), bg="#2c3e50", fg="white").pack(anchor="w",
                                                                                                            padx=50,
                                                                                                            pady=5)
        reg_username = tk.Entry(register_window, font=("Microsoft YaHei", 12), bg="#34495e", fg="white")
        reg_username.pack(fill="x", padx=50, pady=5)

        tk.Label(register_window, text="密码:", font=("Microsoft YaHei", 12), bg="#2c3e50", fg="white").pack(anchor="w",
                                                                                                           padx=50,
                                                                                                           pady=5)
        reg_password = tk.Entry(register_window, show="*", font=("Microsoft YaHei", 12), bg="#34495e", fg="white")
        reg_password.pack(fill="x", padx=50, pady=5)

        tk.Label(register_window, text="确认密码:", font=("Microsoft YaHei", 12), bg="#2c3e50", fg="white").pack(anchor="w",
                                                                                                             padx=50,
                                                                                                             pady=5)
        reg_confirm = tk.Entry(register_window, show="*", font=("Microsoft YaHei", 12), bg="#34495e", fg="white")
        reg_confirm.pack(fill="x", padx=50, pady=5)

        def register():
            username = reg_username.get()
            password = reg_password.get()
            confirm = reg_confirm.get()

            if not username or not password:
                messagebox.showerror("错误", "用户名和密码不能为空")
                return
            if password != confirm:
                messagebox.showerror("错误", "两次输入的密码不一致")
                return
            if username in self.users:
                messagebox.showerror("错误", "用户名已存在")
                return

            self.users[username] = password
            self.save_users()
            messagebox.showinfo("成功", "注册成功")
            register_window.destroy()

        tk.Button(register_window, text="注册", command=register, font=("Microsoft YaHei", 12), bg="#3498db", fg="white",
                  relief="flat", padx=20).pack(pady=20)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if not username or not password:
            messagebox.showerror("错误", "请输入用户名和密码")
            return
        if username in self.users and self.users[username] == password:
            self.current_user = username
            self.create_main_interface()
        else:
            messagebox.showerror("错误", "用户名或密码错误")

    def choose_background(self):
        file_path = filedialog.askopenfilename(filetypes=[("图片文件", "*.jpg;*.jpeg;*.png;*.bmp")])
        if file_path:
            self.set_background(file_path)

    def logout(self):
        self.current_user = None
        self.create_login_screen()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_main_interface(self):
        self.clear_window()
        self.set_background(self.get_user_background_path())

        toolbar = tk.Frame(self.root, bg="#34495e", height=50)
        toolbar.pack(fill="x", padx=10, pady=10)

        user_frame = tk.Frame(toolbar, bg="#34495e")
        user_frame.pack(side="left", padx=10)
        tk.Label(user_frame, text=f"用户: {self.current_user}", font=("Microsoft YaHei", 12), bg="#34495e",
                 fg="white").pack(side="left")

        tk.Button(toolbar, text="登出", command=self.logout, font=("Microsoft YaHei", 12), bg="#e74c3c", fg="white",
                  relief="flat").pack(side="right", padx=10)
        tk.Button(toolbar, text="恢复默认背景", command=lambda: self.set_background(None), font=("Microsoft YaHei", 12),
                  bg="#7f8c8d", fg="white", relief="flat").pack(side="right", padx=10)
        tk.Button(toolbar, text="设置背景", command=self.choose_background, font=("Microsoft YaHei", 12), bg="#34495e",
                  fg="white", relief="flat").pack(side="right", padx=10)

        # 主内容区
        main_frame = tk.Frame(self.root, bg="#2c3e50", bd=0)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # 输入区域
        input_frame = tk.Frame(main_frame, bg="#34495e", padx=20, pady=15)
        input_frame.pack(fill="x", pady=(0, 20))

        tk.Label(input_frame, text="微博链接:", font=("Microsoft YaHei", 12),
                 bg="#34495e", fg="white").grid(row=0, column=0, sticky="w", pady=5)

        self.url_entry = tk.Entry(input_frame, font=("Microsoft YaHei", 12),
                                  bg="#2c3e50", fg="white", width=70)
        self.url_entry.grid(row=0, column=1, padx=10, pady=5, sticky="we")

        # 进度条和状态标签
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(input_frame, variable=self.progress_var,
                                            length=400, mode='determinate')
        self.progress_bar.grid(row=1, column=1, padx=10, pady=5, sticky="we")
        self.progress_var.set(0)

        self.status_label = tk.Label(input_frame, text="就绪", font=("Microsoft YaHei", 10),
                                     bg="#34495e", fg="#f1c40f")
        self.status_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # 分析按钮
        tk.Button(input_frame, text="开始分析", command=self.start_analysis_thread,
                  font=("Microsoft YaHei", 12), bg="#3498db", fg="white",
                  relief="flat", padx=15).grid(row=0, column=2, rowspan=2, padx=10, pady=5)

        # 结果显示区域
        result_frame = tk.Frame(main_frame, bg="#2c3e50")
        result_frame.pack(fill="both", expand=True)

        # 词云显示区域
        wordcloud_frame = tk.LabelFrame(result_frame, text="词云分析", font=("Microsoft YaHei", 12),
                                        bg="#34495e", fg="white", padx=10, pady=10)
        wordcloud_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.wordcloud_panel = tk.Label(wordcloud_frame, bg="#2c3e50")
        self.wordcloud_panel.pack(fill="both", expand=True)

        # 情感分析显示区域
        sentiment_frame = tk.LabelFrame(result_frame, text="情感分布", font=("Microsoft YaHei", 12),
                                        bg="#34495e", fg="white", padx=10, pady=10)
        sentiment_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        self.sentiment_panel = tk.Label(sentiment_frame, bg="#2c3e50")
        self.sentiment_panel.pack(fill="both", expand=True)

        # 底部状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = tk.Label(self.root, textvariable=self.status_var,
                              font=("Microsoft YaHei", 10), bg="#2C3E50", fg="white", anchor="w")
        status_bar.pack(side="bottom", fill="x", padx=10, pady=5)

    def start_analysis_thread(self):
        """启动分析线程"""
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("错误", "请输入微博链接")
            return

        # 禁用分析按钮
        self.status_var.set("开始分析...")
        self.status_label.config(text="开始分析...")
        self.progress_var.set(0)

        # 启动线程
        threading.Thread(target=self.start_analysis, args=(url,), daemon=True).start()

    def start_analysis(self, url):
        """执行分析流程"""
        try:
            # 更新状态
            self.status_var.set("提取微博ID中...")
            self.status_label.config(text="提取微博ID中...")
            self.progress_var.set(10)

            mid = extract_mid_from_url(url)
            if not mid:
                self.status_var.set("错误: 无法提取微博ID")
                messagebox.showerror("错误", "无法从链接中提取微博 mid")
                return

            # 更新状态
            self.status_var.set("获取真实微博ID中...")
            self.status_label.config(text="获取真实微博ID中...")
            self.progress_var.set(20)

            post_id = get_weibo_id_from_mid(mid)
            if not post_id:
                self.status_var.set("错误: 无法获取真实微博ID")
                messagebox.showerror("错误", "无法获取真实微博 ID，可能是 Cookie 失效或 mid 无效")
                return

            # 更新状态
            self.status_var.set(f"爬取评论中... (ID: {post_id})")
            self.status_label.config(text="爬取评论中...")
            self.progress_var.set(30)

            df = get_all_comments(post_id)
            if df is None or df.empty:
                self.status_var.set("错误: 评论爬取失败")
                messagebox.showerror("错误", "评论爬取失败或为空")
                return

            # 保存评论
            os.makedirs("output", exist_ok=True)
            comment_csv_path = "output/comments.csv"
            df.to_csv(comment_csv_path, index=False, encoding="utf-8-sig")

            # 更新状态
            self.status_var.set(f"情感分析中... (共 {len(df)} 条评论)")
            self.status_label.config(text="情感分析中...")
            self.progress_var.set(60)

            df_analyzed = analyze_sentiment(comment_csv_path)

            # 生成可视化结果
            self.status_var.set("生成词云中...")
            self.status_label.config(text="生成词云中...")
            self.progress_var.set(75)

            # ✅ 关键修改：传递停用词文件路径参数
            wordcloud_path = generate_wordcloud(df_analyzed, "stopwords.txt")

            self.status_var.set("生成情感分布图中...")
            self.status_label.config(text="生成情感分布图中...")
            self.progress_var.set(90)
            sentiment_path = plot_sentiment_distribution(df_analyzed)

            # 加载并显示结果
            self.status_var.set("加载分析结果...")
            self.status_label.config(text="加载分析结果...")
            self.progress_var.set(100)

            # 显示词云
            if os.path.exists(wordcloud_path):
                wordcloud_img = Image.open(wordcloud_path)
                wordcloud_img = wordcloud_img.resize((450, 350), Image.LANCZOS)
                self.wordcloud_img = ImageTk.PhotoImage(wordcloud_img)
                self.wordcloud_panel.config(image=self.wordcloud_img)

            # 显示情感分布图
            if os.path.exists(sentiment_path):
                sentiment_img = Image.open(sentiment_path)
                sentiment_img = sentiment_img.resize((450, 350), Image.LANCZOS)
                self.sentiment_img = ImageTk.PhotoImage(sentiment_img)
                self.sentiment_panel.config(image=self.sentiment_img)

            self.status_var.set(f"分析完成! (共 {len(df)} 条评论)")
            self.status_label.config(text="分析完成")

        except Exception as e:
            self.status_var.set(f"错误: {str(e)}")
            self.status_label.config(text="分析出错")
            messagebox.showerror("错误", f"发生错误: {str(e)}")
            # 记录详细错误日志
            with open("error_log.txt", "a") as log:
                log.write(f"{datetime.now()}: {str(e)}\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = WeiboAnalysisApp(root)
    root.mainloop()