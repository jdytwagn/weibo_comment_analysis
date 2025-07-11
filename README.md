# weibo_comment_analysis
Python爬取微博评论+词云分析+情感预测+封装成程序
# 获取cookie
在config.py中的cookie中导入所想要爬取网址的请求标头，以edge浏览器为例，利用F12打开开发者工具，选择网络下拉寻找bulid command...复制其中的请求标头将其放入config.py中即可。获取main.py中Url同理
# 各个文档说明
1.weibo_spider.py为微博抓取页数和解析代码，可以修改代码中的最大抓取页数部分，自定义抓取页码数。
2.sentiment_analysis.py为情感分析代码，主要利用snownlp库和自定义情感倾向文档进行情感分析，融合snownlp判断逻辑和自定义情感倾向文档对评论中词条进行打分大于0.7正向，小于0.3负向，0.3~0.7中性，其可自行设置。其代码中所设置的pos_words.txt文档为正向词文档，neg_words.txt为负向词文档，这两个文档可以自定义设置。
3.visualization.py为可视化词云和情感分析代码。其中pos_words.txt为停用词文档，该文档可自定义，其主要作用即是去掉评论中对于评论主要表达内容无关紧要的词，如助词，语气词等。
4.main.py即是主文件，即是调用上述的代码文件实现所进行的功能。
5.gui_app.py为GUI界面代码，该GUI界面包括注册和登录界面，以及背景自定义界面。进入主界面后输入微博链接即可生成词云分析以及情感预测可视化图。
# GUI封装
主要利用pyinstaller进行封装形成程序，可以通过.exe文件直接打开该微博评论情感分析系统而不用进行代码的交互与运行。
步骤：首先cd到自己的项目空间中，通过pyinstaller --onefile --windowed --name="微博评论情感分析系统"  gui_app.py即可实现打包。如果出现未打包文件的错误，可以在形成的微博评论情感分析系统.spec文档中进行添加修改（在此中便于修改），修改完成后输入pyinstaller 微博评论情感分析系统.spec即可打包。

<img width="1795" height="1237" alt="image" src="https://github.com/user-attachments/assets/f00e95b3-a4d9-46ee-8153-3df694e9d090" />

<img width="2526" height="1470" alt="image" src="https://github.com/user-attachments/assets/b1fb3c69-5e48-4ffd-8d36-766c4c5f994f" />

<img width="1794" height="1234" alt="image" src="https://github.com/user-attachments/assets/b851e566-9ead-472e-bfa6-ad5f6e6f09fb" />




# 自定义图标
形成的.exe文件可以自定义快捷方式的图标。但图标的格式必须是.ico格式，在快捷方式的属性中更改图标方式进行修改即可。

<img width="138" height="156" alt="image" src="https://github.com/user-attachments/assets/0b6a05fb-15f8-4b35-b87f-2771500e240b" />








