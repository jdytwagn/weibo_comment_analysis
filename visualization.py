from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import jieba
import matplotlib
import re
import os

matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体为黑体
matplotlib.rcParams['axes.unicode_minus'] = False  # 正确显示负号

# 全局缓存停用词
STOPWORDS_CACHE = None


def load_stopwords(path="stopwords.txt"):
    global STOPWORDS_CACHE
    if STOPWORDS_CACHE is not None:
        return STOPWORDS_CACHE

    try:
        if not os.path.exists(path):
            raise FileNotFoundError(f"停用词文件不存在: {path}")

        with open(path, "r", encoding="utf-8") as f:
            STOPWORDS_CACHE = set(f.read().splitlines())
            print(f"成功加载停用词: {len(STOPWORDS_CACHE)} 个")
            return STOPWORDS_CACHE
    except Exception as e:
        print(f"停用词加载错误: {str(e)}")
        # 返回基础停用词作为后备
        return {"的", "了", "是", "在", "和", "就", "都", "而", "及", "与"}


def clean_text(text):
    # 去除 HTML 标签、表情、链接等
    text = re.sub(r"<.*?>", "", text)  # 去掉 <img> <a> 等标签
    text = re.sub(r"http\S+", "", text)  # 去掉链接
    text = re.sub(r"[a-zA-Z0-9]", "", text)  # 去掉英文字母和数字
    text = re.sub(r"[^\u4e00-\u9fa5]", "", text)  # 去掉非中文字符
    return text


def generate_wordcloud(df, stopwords_path="stopwords.txt"):
    # 加载停用词
    stopwords = load_stopwords(stopwords_path)

    # 清洗文本
    cleaned_comments = df["text"].astype(str).apply(clean_text)

    # 分词 + 停用词过滤
    words = jieba.cut(" ".join(cleaned_comments))
    filtered_words = [word for word in words if word not in stopwords and len(word) > 1]

    if not filtered_words:
        raise ValueError("过滤后无有效词汇，请检查停用词配置或文本内容")

    text = " ".join(filtered_words)

    # 生成词云
    wc = WordCloud(
        font_path="C:/Windows/Fonts/simhei.ttf",  # 替换为你的 simhei.ttf 路径
        background_color="white",
        width=800,
        height=400,
        max_words=200,
        collocations=False  # 禁用词频优化提升性能
    ).generate(text)

    # 保存词云
    plt.figure(figsize=(10, 5))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.title("微博评论词云")
    plt.tight_layout()
    plt.savefig("wordcloud.png", dpi=300, bbox_inches='tight')
    plt.close()  # 关闭图形避免内存泄漏
    return "wordcloud.png"


def plot_sentiment_distribution(df):
    sentiment_count = Counter(df["sentiment_label"])
    plt.figure(figsize=(6, 4))
    plt.bar(
        sentiment_count.keys(),
        sentiment_count.values(),
        color=["green", "grey", "red"]
    )
    plt.title("情感分布图")
    plt.ylabel("评论数量")
    plt.savefig("sentiment_bar.png", bbox_inches='tight')
    plt.close()  # 关闭图形避免内存泄漏
    return "sentiment_bar.png"