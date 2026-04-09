"""
AI新闻聚合系统配置文件
"""

# QQ邮箱配置
QQ_EMAIL = "1092604093@qq.com"
QQ_AUTH_CODE = "ipupupwzvomqjiae"  # 需要替换为实际的授权码

# 第二个QQ邮箱配置
QQ_EMAIL2 = "xianghongyuan@vip.qq.com"
QQ_AUTH_CODE2 = "jopjgqdvscpmbebe"

# SMTP服务器配置
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465

# 爬虫配置
REQUEST_TIMEOUT = 10
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# 数据源配置 - 优质内容源汇总
DATA_SOURCES = {
    'domestic': {  # 国内优质新闻源（专业科技媒体 + 行业大V）
        '机器之心': 'https://www.jiqizhixin.com/feed',  # AI领域最专业
        '量子位': 'https://www.qbitai.com/feed',         # 深度技术分析
        'AI科技大本营': 'https://www.infoq.cn/feed/ai',   # InfoQ旗下，企业级内容
        '新智元': 'https://feeds.lanxiniu.com/rss/xinzhiyuan', # AI产业观察
        'AI前线': 'https://www.infoq.cn/feed/ai',        # 高质量技术文章
    },
    'international': {  # 国际优质新闻源（官方发布 + 权威论坛）
        'Hacker News': 'https://hacker-news.firebaseio.com/v0',  # 硅谷技术社区
        'Product Hunt': 'https://www.producthunt.com/feed/upcoming', # 新产品发布
        'TechCrunch': 'https://feeds.techcrunch.com/techcrunch/',   # 科技新闻权威
        'The Verge AI': 'https://www.theverge.com/ai-artificial-intelligence/rss/index.xml',
        'VentureBeat': 'https://feeds.venturebeat.com/feed/',      # AI融资和动态
    },
    'academic': {  # 学术论文（顶级会议 + 研究机构）
        'arXiv AI': 'http://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=submittedDate&sortOrder=descending',
        'arXiv ML': 'http://export.arxiv.org/api/query?search_query=cat:cs.LG&sortBy=submittedDate&sortOrder=descending',
        'Papers with Code': 'https://paperswithcode.com/rss.xml',  # 有代码的论文
    },
    'official': {  # 官方权威发布（Big Tech + 研究机构）
        'OpenAI Blog': 'https://openai.com/blog/rss/',
        'DeepMind Blog': 'https://www.deepmind.com/blog/rss',
        'Google AI': 'https://ai.googleblog.com/feeds/posts/default/-/ai',
        'Meta AI': 'https://ai.meta.com/blog/feed/',
        'Anthropic': 'https://www.anthropic.com/feed.xml',         # Claude母公司
        'Microsoft Research': 'https://www.microsoft.com/en-us/research/feed/?region=en-us',
        'Stanford HAI': 'https://hai.stanford.edu/feed',           # 斯坦福AI指数
    },
    'research': {  # 研究机构 + 智库
        'OpenAI Research': 'https://openai.com/research/rss/',
        'Berkeley AI': 'https://bair.berkeley.edu/blog/feed.xml',  # 伯克利AI研究所
        'MIT CSAIL': 'https://www.csail.mit.edu/news/feed/',       # MIT计算机科学与AI实验室
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
