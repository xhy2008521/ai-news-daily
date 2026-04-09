"""
AI新闻聚合系统配置文件
"""

# QQ邮箱配置
QQ_EMAIL = "1092604093@qq.com"
QQ_AUTH_CODE = "ipupupwzvomqjiae"  # 需要替换为实际的授权码

# SMTP服务器配置
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465

# 爬虫配置
REQUEST_TIMEOUT = 10
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# 数据源配置
DATA_SOURCES = {
    'domestic': {  # 国内新闻源
        '36氪': 'https://36kr.com/feed',
        '量子位': 'https://www.qbitai.com/feed',
        '机器之心': 'https://www.jiqizhixin.com/feed',
    },
    'international': {  # 国际新闻源
        'Product Hunt': 'https://api.producthunt.com/v2/api',
        'Hacker News': 'https://hacker-news.firebaseio.com/v0',
    },
    'academic': {  # 学术论文
        'arxiv': 'http://export.arxiv.org/api/query',
    },
    'official': {  # 官方发布
        'OpenAI Blog': 'https://openai.com/blog/rss/',
        'Google AI': 'https://ai.googleblog.com/feeds/posts/default/-/ai',
        'Meta AI': 'https://ai.meta.com/blog/feed/',
    }
}

# 日志配置
LOG_DIR = './logs'
LOG_FILE = './logs/ai_news.log'

# 数据库配置
DB_PATH = './data/news_cache.db'

# 邮件配置
EMAIL_SUBJECT_PREFIX = "🤖 AI新闻日报 -"
EMAIL_FROM = QQ_EMAIL
EMAIL_TO = QQ_EMAIL

# 时间配置
TIMEZONE = 'Asia/Shanghai'
SEND_HOUR = 8
SEND_MINUTE = 0
