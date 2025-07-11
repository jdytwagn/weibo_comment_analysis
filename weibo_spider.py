import requests
import pandas as pd
import time
from config import headers, comment_api

def get_weibo_id_from_mid(mid):
    url = f"https://weibo.com/ajax/statuses/show?id={mid}"
    resp = requests.get(url, headers=headers)
    try:
        return resp.json()["id"]
    except:
        print("❌ 获取微博真实 ID 失败，可能是 Cookie 失效或 mid 无效")
        return None

def extract_mid_from_url(url):
    import re
    m = re.search(r'/(\w+)\?', url)
    if not m:
        m = re.search(r'/(\w+)$', url)
    return m.group(1) if m else None

def get_all_comments(post_id):
    all_comments = []
    max_id = 0
    page = 1

    while True:
        url = comment_api.format(post_id, max_id)
        resp = requests.get(url, headers=headers)

        print(f"\n[第{page}页] 请求 URL: {url}")
        print(f"[状态码] {resp.status_code}")

        try:
            data = resp.json()
        except Exception as e:
            print(f"❌ 第{page}页 JSON解析失败: {e}")
            break

        if data.get("ok") != 1:
            print("⚠️ 数据返回异常，终止")
            break

        # ✅ 核心修改：兼容 data 是 dict 或 list 的情况
        comments_data = []
        if isinstance(data.get("data"), dict):
            comments_data = data["data"].get("data", [])
            max_id = data["data"].get("max_id", 0)
        elif isinstance(data.get("data"), list):
            comments_data = data["data"]
            max_id = data.get("max_id", 0)
        else:
            print(f"⚠️ 第{page}页结构异常，data字段既不是字典也不是列表")
            break

        if not comments_data:
            print("✅ 没有更多评论，结束爬取")
            break

        for comment in comments_data:
            try:
                all_comments.append({
                    "user": comment["user"]["screen_name"],
                    "text": comment["text"],
                    "like": comment.get("like_count", 0)
                })
            except Exception as e:
                print(f"⚠️ 跳过异常评论：{e}")

        print(f"✅ 成功抓取第{page}页评论，累计数：{len(all_comments)}")

        if max_id == 0:
            print("✅ 无法继续翻页，评论已全部抓取完毕")
            break

        page += 1
        time.sleep(1.5)

    df = pd.DataFrame(all_comments)
    df.to_csv("comments.csv", index=False, encoding='utf-8-sig')
    print("📁 已保存到 comments.csv")
    return df