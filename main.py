from weibo_spider import extract_mid_from_url, get_weibo_id_from_mid, get_all_comments
from sentiment_analysis import analyze_sentiment_with_hybrid as analyze_sentiment
from visualization import generate_wordcloud, plot_sentiment_distribution
import os

def main():
    url = "https://weibo.com/1776448504/PtK63r5zG?pagetype=profilefeed"
    mid = extract_mid_from_url(url)
    print(f"[0] 提取到微博 mid: {mid}")
    post_id = get_weibo_id_from_mid(mid)
    if not post_id:
        print("❌ 无法获取真实微博 ID，程序终止")
        return

    print(f"[1] 正在爬取微博评论：{post_id}")
    df = get_all_comments(post_id)

    if df is None or df.empty:
        print("❌ 评论爬取失败或为空，程序终止")
        return

    # 保存评论
    os.makedirs("output", exist_ok=True)
    comment_csv_path = "output/comments.csv"
    df.to_csv(comment_csv_path, index=False, encoding="utf-8-sig")

    print(f"[2] 正在进行情感分析...")
    df_analyzed = analyze_sentiment(comment_csv_path)

    print(f"[3] 正在生成词云与情感分布图...")
    stopwords = set()
    if os.path.exists("stopwords.txt"):
        from visualization import load_stopwords
        stopwords = load_stopwords()
    generate_wordcloud(df_analyzed, stopwords)
    plot_sentiment_distribution(df_analyzed)

    print("✅ 所有流程已完成，结果保存在当前目录下")

if __name__ == "__main__":
    main()