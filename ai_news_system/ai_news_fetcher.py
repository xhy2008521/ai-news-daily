"""
AI新闻爬取模块 - 从各个数据源收集新闻（自动翻译为中文）
"""
import requests
import feedparser
import re
import time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging
import config

logger = logging.getLogger(__name__)


def translate_to_chinese(text):
    """使用免费翻译 API 将英文翻译为中文"""
    if not text or len(text) < 5:
        return text

    # 检测是否为中文
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    if chinese_chars > len(text) * 0.3:
        return text  # 已包含大量中文

    try:
        # MyMemory 免费翻译 API（无需 API key）
        url = 'https://api.mymemory.translated.net/get'
        params = {
            'q': text[:500],  # 限制长度
            'langpair': 'en|zh-CN'
        }
        resp = requests.get(url, params=params, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            translated = data.get('responseData', {}).get('translatedText', '')
            if translated and translated != text:
                return translated
    except Exception:
        pass

    # 翻译失败时返回原文，标记 [英]
    return '[英] ' + text


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
        self.fetch_research_news()

        # 去重和排序
        self.news_list = self._deduplicate_and_sort(self.news_list)

        logger.info(f"爬取完成，共获得 {len(self.news_list)} 条新闻（已去重）")
        return self.news_list

    def _deduplicate_and_sort(self, news_list):
        """去重和排序新闻"""
        # 按URL去重（核心：相同URL视为重复）
        seen_urls = set()
        deduplicated = []

        for news in news_list:
            url = news.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                deduplicated.append(news)

        # 按重要性排序：官方发布 > 论文研究 > 国际新闻 > 国内新闻
        source_priority = {
            'OpenAI Blog': 100,
            'OpenAI Research': 100,
            'DeepMind Blog': 95,
            'Google AI': 90,
            'Google Research': 90,
            'Meta AI': 85,
            'Microsoft Research': 85,
            'Anthropic': 85,
            'Stanford HAI': 80,
            'Berkeley AI': 80,
            'MIT CSAIL': 80,
            'Papers with Code': 75,
            'arXiv': 70,
            'TechCrunch': 65,
            'VentureBeat': 60,
            'Hacker News': 55,
            '机器之心': 50,
            '量子位': 48,
        }

        # 添加优先级字段
        for news in deduplicated:
            source = news.get('source', '')
            priority = source_priority.get(source, 0)
            news['priority'] = priority

        # 按优先级降序排序
        sorted_news = sorted(deduplicated, key=lambda x: (-x.get('priority', 0), x.get('source', '')))

        return sorted_news

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

    def fetch_research_news(self):
        """爬取研究机构发布"""
        logger.info("爬取研究机构...")

        sources = config.DATA_SOURCES.get('research', {})
        for source_name, rss_url in sources.items():
            try:
                self._fetch_rss(rss_url, source_name, '研究机构')
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
                    # 翻译标题和摘要
                    translated_title = translate_to_chinese(title)
                    translated_summary = translate_to_chinese(summary[:200])

                    news = {
                        'category': category,
                        'title': translated_title,
                        'summary': translated_summary,
                        'url': url,
                        'source': source_name,
                        'original_title': title if translated_title != title else '',
                        'original_summary': summary[:200] if translated_summary != summary[:200] else '',
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
                        translated_title = translate_to_chinese(title)
                        score_cn = translate_to_chinese(
                            f"({story.get('score', 0)} points, {story.get('descendants', 0)} comments)"
                        )
                        news = {
                            'category': '国际新闻',
                            'title': translated_title,
                            'summary': score_cn,
                            'url': story_link,
                            'source': 'Hacker News',
                            'original_title': title if translated_title != title else '',
                            'original_summary': '',
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
                    translated_title = translate_to_chinese(title)
                    authors = ', '.join([author.name for author in entry.authors[:3]])
                    news = {
                        'category': '学术论文',
                        'title': translated_title,
                        'summary': f"作者: {authors}",
                        'url': url_paper,
                        'source': 'arXiv',
                        'original_title': title if translated_title != title else '',
                        'original_summary': '',
                    }
                    self.news_list.append(news)
                    self.db.add_news(url_paper, title, '学术论文', 'arXiv')
                    count += 1

            logger.info(f"arXiv: 获得 {count} 条新论文")

        except Exception as e:
            logger.error(f"arXiv爬取失败: {str(e)}")
