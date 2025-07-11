import os
import pandas as pd
from snownlp import SnowNLP
import jieba


def load_sentiment_words(pos_path="pos_words.txt", neg_path="neg_words.txt"):
    """加载正向与负向情感词"""
    def load_words(path):
        if not os.path.exists(path):
            return set()
        with open(path, "r", encoding="utf-8") as f:
            return set(f.read().splitlines())
    return load_words(pos_path), load_words(neg_path)


def classify_with_dict(text, pos_words, neg_words):
    """基于情感词典的简单情感判断"""
    words = jieba.lcut(text)
    pos_count = sum(1 for w in words if w in pos_words)
    neg_count = sum(1 for w in words if w in neg_words)

    if pos_count > neg_count:
        return "正面"
    elif neg_count > pos_count:
        return "负面"
    else:
        return "中性"


def analyze_sentiment_with_hybrid(input_csv="comments.csv", output_csv="output/comments_analyzed.csv"):
    """混合式情感分析：SnowNLP + 情感词典 双策略融合"""
    # 输入校验
    if not os.path.exists(input_csv) or os.path.getsize(input_csv) == 0:
        raise FileNotFoundError(f"输入文件 {input_csv} 不存在或为空，请检查评论是否成功爬取。")

    df = pd.read_csv(input_csv)
    if "text" not in df.columns:
        raise ValueError("CSV 文件中不包含 'text' 列，请检查爬虫输出格式")

    # 加载情感词典
    pos_words, neg_words = load_sentiment_words()

    sentiment_scores = []
    sentiment_labels = []

    # 遍历评论进行情感分析
    for text in df["text"]:
        try:
            # SnowNLP 预测情感得分
            s = SnowNLP(text)
            score = s.sentiments
            label_snow = (
                "正面" if score > 0.7 else
                "负面" if score < 0.3 else
                "中性"
            )

            # 词典规则判断
            label_dict = classify_with_dict(text, pos_words, neg_words)

            # 融合逻辑
            if 0.3 <= score <= 0.7:
                final_label = label_dict  # 中间分数靠词典判断
            else:
                # 冲突处理：如果 SnowNLP 与词典结果冲突，信任词典
                final_label = label_dict if (label_dict != "中性" and label_dict != label_snow) else label_snow

            sentiment_scores.append(score)
            sentiment_labels.append(final_label)

        except Exception:
            sentiment_scores.append(0.5)
            sentiment_labels.append("中性")

    # 添加情感列到 DataFrame
    df["sentiment_score"] = sentiment_scores
    df["sentiment_label"] = sentiment_labels

    # 保存分析结果
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"✅ 分析完成，结果保存至 {output_csv}")

    return df
