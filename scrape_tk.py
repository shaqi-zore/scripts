import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 目标发卡站分类链接
TARGET_URL = "https://tkhao.top/?cid=3"
OUTPUT_FILE = "tk_inventory.json"

def fetch_inventory():
    # 模拟真实浏览器请求，防止被简单的防火墙拦截
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }

    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=15)
        response.encoding = 'utf-8' # 确保中文不乱码
        response.raise_for_status()
    except Exception as e:
        print(f"[Error] 请求目标网站失败: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    products = []

    # 兼容常见的发卡站页面结构（列表组或表格行）
    # 如果运行后抓不到数据，需在浏览器按 F12 审查元素，替换下方的 class 或标签名
    items = soup.select(".list-group-item, .goods-item, .layui-table tbody tr")

    for item in items:
        # 提取商品名称、价格、库存
        name_el = item.select_one(".name, .goods-name, td:nth-child(1)")
        price_el = item.select_one(".price, .text-danger, td:nth-child(2)")
        stock_el = item.select_one(".stock, .badge, td:nth-child(3)")

        if name_el and price_el:
            products.append({
                "name": name_el.get_text(strip=True),
                "price": price_el.get_text(strip=True).replace('￥', '').replace('元', ''),
                "stock": stock_el.get_text(strip=True) if stock_el else "未知"
            })

    return {
        "update_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "source_url": TARGET_URL,
        "count": len(products),
        "data": products
    }

def main():
    data = fetch_inventory()
    if data and data["count"] > 0:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[Success] 成功抓取 {data['count']} 条库存数据并保存至 {OUTPUT_FILE}")
    else:
        print("[Warning] 未抓取到有效数据。请检查该网站是否开启了防爬盾，或者数据是由 Ajax 异步加载的。")

if __name__ == "__main__":
    main()
