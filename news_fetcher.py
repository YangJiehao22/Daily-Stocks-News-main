import requests
import json
import feedparser
from datetime import datetime
from typing import List, Dict
import hashlib


DEFAULT_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    ),
}


class NVIDIANewsFetcher:
    def __init__(self):
        self.news_list = []

        # NVIDIA and AI-related keywords
        self.nvidia_keywords = [
            'NVIDIA', 'nvidia', '英伟达', 'Nvidia',
            'GPU', 'AI', 'artificial intelligence',
            'H100', 'A100', 'L40', 'H200', 'Blackwell', 'CUDA',
            'data center', '数据中心', '算力', '大模型', '智算',
            'chip', '芯片', 'semiconductor', '半导体',
            'machine learning', 'deep learning', '深度学习',
            'transformer', 'LLM', '服务器', '液冷',
        ]

        # China-listed companies in NVIDIA supply chain
        self.china_companies = {
            '芯片制造': ['中芯国际', 'SMIC', 'Semiconductor Manufacturing International',
                       '安集微电子', '晶方科技', '长川科技', '华峰测控',
                       '兆易创新', 'GigaDevice', '韦尔股份'],
            '散热冷却': ['九州风神', 'Deepcool', '法拉电子'],
            'PCB材料': ['生益科技', '金安国纪', '上海新昇'],
            'AI平台': ['浪潮信息', 'Inspur', '中科曙光', 'Sugon', '商汤科技', 'SenseTime'],
            '互联网': ['华为', 'Huawei', '阿里', 'Alibaba', '腾讯', 'Tencent',
                     '百度', 'Baidu', '字节跳动', 'ByteDance', 'JiuZhou'],
        }

        # (url, skip_filter) - domestic feeds first for users in China
        self.rss_feeds = [
            ('https://www.ithome.com/rss/', False),
            ('https://36kr.com/feed', False),
            ('https://www.jiqizhixin.com/rss', False),
            ('https://www.leiphone.com/feed', False),
            ('https://rss.sina.com.cn/tech/rollnews.xml', False),
            ('https://feeds.reuters.com/reuters/technologyNews', False),
            ('https://feeds.bloomberg.com/technology/news.rss', False),
            ('https://www.cnbc.com/id/100003114/device/rss/rss.html', False),
        ]

    def is_relevant_news(self, title: str, description: str = '') -> bool:
        """Check if news is relevant to NVIDIA supply chain"""
        text = (title + ' ' + description).lower()

        nvidia_match = any(kw.lower() in text for kw in self.nvidia_keywords)

        company_match = False
        for companies in self.china_companies.values():
            if any(comp.lower() in text for comp in companies):
                company_match = True
                break

        return nvidia_match or company_match

    def _parse_feed(self, feed_url: str):
        """Fetch RSS with browser-like headers for better compatibility."""
        try:
            response = requests.get(feed_url, headers=DEFAULT_HEADERS, timeout=15)
            response.raise_for_status()
            return feedparser.parse(response.content)
        except requests.RequestException as e:
            print(f"  Request failed: {e}")
            return feedparser.parse(b'')

    def fetch_from_rss(self) -> List[Dict]:
        """Fetch news from RSS feeds"""
        articles = []

        for feed_url, skip_filter in self.rss_feeds:
            try:
                print(f"Fetching from: {feed_url}")
                feed = self._parse_feed(feed_url)
                total_entries = len(feed.entries)

                if feed.bozo and feed.bozo_exception:
                    print(f"  Parse warning: {feed.bozo_exception}")

                matched = 0
                for entry in feed.entries[:30]:
                    title = entry.get('title', '')
                    summary = entry.get('summary', entry.get('description', ''))
                    link = entry.get('link', '')
                    published = entry.get('published', datetime.now().isoformat())

                    if skip_filter or self.is_relevant_news(title, summary):
                        matched += 1
                        articles.append({
                            'title': title,
                            'description': summary[:250] if summary else '',
                            'url': link,
                            'publishedAt': published,
                            'source': {'name': feed.feed.get('title', 'RSS Feed')},
                            'hash': hashlib.md5(title.encode()).hexdigest(),
                        })

                print(f"  {total_entries} entries, {matched} matched")

            except Exception as e:
                print(f"Error fetching from {feed_url}: {e}")
                continue

        print(f"Fetched {len(articles)} articles from RSS feeds")
        return articles
    
    def deduplicate_news(self, news_list: List[Dict]) -> List[Dict]:
        """Remove duplicate news items"""
        seen_hashes = set()
        unique = []
        
        for item in news_list:
            item_hash = item.get('hash') or hashlib.md5(item.get('title', '').encode()).hexdigest()
            
            if item_hash not in seen_hashes:
                seen_hashes.add(item_hash)
                unique.append(item)
        
        return unique
    
    def sort_news(self, news_list: List[Dict]) -> List[Dict]:
        """Sort news by publish date (newest first)"""
        try:
            return sorted(
                news_list,
                key=lambda x: x.get('publishedAt', ''),
                reverse=True
            )
        except:
            return news_list
    
    def fetch_all_news(self, max_items: int = 20) -> List[Dict]:
        """Fetch and process all news"""
        print(f"Fetching NVIDIA supply chain news...")
        
        # Fetch from RSS
        self.news_list.extend(self.fetch_from_rss())
        
        # Deduplicate
        self.news_list = self.deduplicate_news(self.news_list)
        
        # Sort by date
        self.news_list = self.sort_news(self.news_list)
        
        # Limit to max items
        self.news_list = self.news_list[:max_items]
        
        print(f"Total {len(self.news_list)} unique news items retrieved")
        return self.news_list
    
    def save_to_file(self, filename: str = 'daily_news.json'):
        """Save news to JSON file"""
        output_data = {
            'timestamp': datetime.now().isoformat(),
            'count': len(self.news_list),
            'news': self.news_list
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            print(f"✅ News saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving news: {e}")


if __name__ == '__main__':
    print("=" * 60)
    print("NVIDIA AI Server Supply Chain News Fetcher")
    print("=" * 60)
    
    fetcher = NVIDIANewsFetcher()
    fetcher.fetch_all_news(max_items=20)
    fetcher.save_to_file()
    
    print("=" * 60)
    print(f"Fetched {len(fetcher.news_list)} news items")
    print("=" * 60)
