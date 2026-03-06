"""
Binance Alpha Radar - 币安公告探测雷达
监控新币上线/重大公告，第一时间获取Alpha
"""
import requests
import time
from datetime import datetime
from typing import List, Dict

# Binance Announcement APIs
BINANCE_NEWS_URL = "https://www.binance.com/bapi/cms/v1/article/list"

def get_binance_announcements(catalog_id: int = 48, limit: int = 10) -> List[Dict]:
    """
    获取币安公告
    catalog_id:
    - 48: 新币上线/Launchpool
    - 49: 重大公告
    - 50: 市场公告
    """
    params = {
        "catalogId": catalog_id,
        "pageNo": 1,
        "pageSize": limit
    }
    
    try:
        resp = requests.get(BINANCE_NEWS_URL, params=params, timeout=10)
        data = resp.json()
        
        articles = []
        for item in data.get("data", {}).get("articles", []):
            articles.append({
                "title": item.get("title", ""),
                "article_id": item.get("articleId", ""),
                "publish_date": item.get("publishDate", ""),
                "url": f"https://www.binance.com/en/support/announcement/detail/{item.get('articleId', '')}",
                "catalog_id": catalog_id
            })
        
        return articles
        
    except Exception as e:
        print(f"Error fetching announcements: {e}")
        return []

def get_new_listings(limit: int = 5) -> List[Dict]:
    """获取新币上线公告 (catalogId=48)"""
    return get_binance_announcements(48, limit)

def get_major_news(limit: int = 5) -> List[Dict]:
    """获取重大公告 (catalogId=49)"""
    return get_binance_announcements(49, limit)

def get_alpha_signals() -> str:
    """生成 Alpha 信号报告"""
    listings = get_new_listings(5)
    news = get_major_news(5)
    
    msg = "🎯 *Binance Alpha 探测雷达*\n\n"
    
    # New Listings
    if listings:
        msg += "🚀 *新币上线*\n"
        for item in listings:
            msg += f"• {item['title']}\n"
            msg += f"  {item['publish_date']}\n\n"
    else:
        msg += "🚀 *新币上线*: 暂无\n\n"
    
    # Major News
    if news:
        msg += "📢 *重大公告*\n"
        for item in news[:3]:
            msg += f"• {item['title']}\n"
            msg += f"  {item['publish_date']}\n\n"
    
    msg += f"⏰ 更新时间: {datetime.now().strftime('%H:%M:%S')}"
    
    return msg


# RSS Feed Aggregation
RSS_FEEDS = {
    "AI": [
        "https://rss.nytimes.com/services/xml/rss/nyt/ArtificialIntelligence.xml",
        "https://www.wired.com/feed/tag/ai/latest/rss",
    ],
    "Crypto": [
        "https://cointelegraph.com/rss",
        "https://decrypt.co/feed",
    ],
    "Tech": [
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml",
    ]
}

def fetch_rss(url: str, limit: int = 5) -> List[Dict]:
    """抓取 RSS 源"""
    try:
        resp = requests.get(url, timeout=10)
        # Simple parsing - in production use feedparser
        return [{"title": "RSS Item", "url": url}]
    except:
        return []

def get_news_briefing() -> str:
    """生成新闻简报"""
    msg = "📰 *AI + Crypto 早报*\n\n"
    
    for category, feeds in RSS_FEEDS.items():
        msg += f"**{category}**\n"
        for feed in feeds:
            msg += f"• {feed}\n"
        msg += "\n"
    
    msg += "---\n"
    msg += get_alpha_signals()
    
    return msg


# Main
if __name__ == "__main__":
    print("🎯 Binance Alpha Radar")
    print("="*50)
    print(get_alpha_signals())
