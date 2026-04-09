"""
AI新闻爬取模块 - 从各个数据源收集新闻
"""
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging
import config

logger = logging.getLogger(__name__)


class NewsAggregator:
    def __init__(self, db):
        self.db = db
        self.news_list = []

    def fetch_all_news(self):
        """从所有数据源获取新闻"""
        logger.info("开始爬取新闻...")

        self.fetch_domestic_news()
        self.fetch_international_news()
        self.fetch_academic_news()
        self.fetch_official_news()

        logger.info(f"爬取完成，共获得 {len(self.news_list)} 条新闻")
        return self.news_list

    def fetch_domestic_news(self):
        """爬取国内新闻源"""
        logger.info("爬取国内新闻源...")

        sources = config.DATA_SOURCES.get('domestic', {})
        for source_name, rss_url in sources.items():
            try:
                self._fetch_rss(rss_url, source_name, '国内新闻')
            except Exception as e:
                logger.warning(f"爬取{source_name}失败: {str(e)}")

    def fetch_international_news(self):
        """爬取国际新闻源"""
        logger.info("爬取国际新闻源...")

        # Product Hunt API
        try:
            self._fetch_producthunt()
        except Exception as e:
            logger.warning(f"爬取Product Hunt失败: {str(e)}")

        # Hacker News
        try:
            self._fetch_hackernews()
        except Exception as e:
            logger.warning(f"爬取Hacker News失败: {str(e)}")

    def fetch_academic_news(self):
        """爬取学术论文"""
        logger.info("爬取学术论文...")

        try:
            self._fetch_arxiv()
        except Exception as e:
            logger.warning(f"爬取arxiv失败: {str(e)}")

    def fetch_official_news(self):
        """爬取官方Blog"""
        logger.info("爬取官方Blog...")

        sources = config.DATA_SOURCES.get('official', {})
        for source_name, rss_url in sources.items():
            try:
                self._fetch_rss(rss_url, source_name, '官方发布')
            except Exception as e:
                logger.warning(f"爬取{source_name}失败: {str(e)}")

    def _fetch_rss(self, rss_url, source_name, category):
        """通用RSS爬取方法"""
        try:
            response = requests.get(rss_url, headers=config.REQUEST_HEADERS, timeout=config.REQUEST_TIMEOUT)
            response.encoding = 'utf-8'
            feed = feedparser.parse(response.content)

            count = 0
            for entry in feed.entries[:10]:  # 限制每个源最多10条
                url = entry.get('link', '')
                title = entry.get('title', '').strip()
                summary = entry.get('summary', '暂无摘要').strip()

                # 清理摘要HTML标签
                if '<' in summary:
                    soup = BeautifulSoup(summary, 'html.parser')
                    summary = soup.get_text()[:100]

                if url and not self.db.is_news_pushed(url):
                    news = {
                        'category': category,
                        'title': title,
                        'summary': summary,
                        'url': url,
                        'source': source_name
                    }
                    self.news_list.append(news)
                    self.db.add_news(url, title, category, source_name)
                    count += 1

            logger.info(f"{source_name}: 获得 {count} 条新新闻")

        except Exception as e:
            logger.error(f"RSS爬取失败 {source_name}: {str(e)}")

    def _fetch_producthunt(self):
        """爬取Product Hunt (简化版本 - 需要API Key)"""
        # 注：需要从Product Hunt获取API key才能使用
        logger.debug("Product Hunt爬取暂时跳过（需要API Key）")
        pass

    def _fetch_hackernews(self):
        """爬取Hacker News最新AI相关讨论"""
        try:
            # 获取最新的story ID
            url = 'https://hacker-news.firebaseio.com/v0/topstories.json'
            response = requests.get(url, timeout=config.REQUEST_TIMEOUT)
            story_ids = response.json()[:30]  # 获取前30个

            count = 0
            for story_id in story_ids[:10]:  # 限制处理前10个
                story_url = f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json'
                story = requests.get(story_url, timeout=config.REQUEST_TIMEOUT).json()

                if story.get('deleted') or story.get('dead'):
                    continue

                title = story.get('title', '').strip()
                if any(keyword in title.lower() for keyword in ['ai', 'ml', 'llm', 'gpt', '机器学习', '人工智能']):
                    story_link = story.get('url', f"https://news.ycombinator.com/item?id={story_id}")
                    if story_link and not self.db.is_news_pushed(story_link):
                        news = {
                            'category': '国际新闻',
                            'title': title,
                            'summary': f"({story.get('score', 0)} points, {story.get('descendants', 0)} comments)",
                            'url': story_link,
                            'source': 'Hacker News'
                        }
                        self.news_list.append(news)
                        self.db.add_news(story_link, title, '国际新闻', 'Hacker News')
                        count += 1

            logger.info(f"Hacker News: 获得 {count} 条新新闻")

        except Exception as e:
            logger.error(f"Hacker News爬取失败: {str(e)}")

    def _fetch_arxiv(self):
        """爬取arxiv最新AI/ML论文"""
        try:
            # 查询最新的AI/深度学习/机器学习论文
            url = 'http://export.arxiv.org/api/query'
            params = {
                'search_query': 'cat:cs.AI OR cat:cs.LG AND submittedDate:[' +
                               (datetime.now() - timedelta(days=1)).strftime('%Y%m%d') + '000000 TO ' +
                               datetime.now().strftime('%Y%m%d') + '235959]',
                'sortBy': 'submittedDate',
                'sortOrder': 'descending',
                'max_results': 15
            }

            response = requests.get(url, params=params, timeout=config.REQUEST_TIMEOUT)
            response.encoding = 'utf-8'
            feed = feedparser.parse(response.content)

            count = 0
            for entry in feed.entries:
                arxiv_id = entry.id.split('/abs/')[-1]
                title = entry.title.strip()
                url_paper = f"https://arxiv.org/abs/{arxiv_id}"

                if not self.db.is_news_pushed(url_paper):
                    authors = ', '.join([author.name for author in entry.authors[:3]])
                    news = {
                        'category': '学术论文',
                        'title': title,
                        'summary': f"作者: {authors}",
                        'url': url_paper,
                        'source': 'arXiv'
                    }
                    self.news_list.append(news)
                    self.db.add_news(url_paper, title, '学术论文', 'arXiv')
                    count += 1

            logger.info(f"arXiv: 获得 {count} 条新论文")

        except Exception as e:
            logger.error(f"arXiv爬取失败: {str(e)}")
