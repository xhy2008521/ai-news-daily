"""
SQLite数据库操作模块 - 用于存储已推送的新闻，实现去重
"""
import sqlite3
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class NewsDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 创建新闻表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    category TEXT,
                    source TEXT,
                    push_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_url ON news(url)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_push_time ON news(push_time)')

            conn.commit()
            conn.close()
            logger.info("数据库初始化成功")
        except Exception as e:
            logger.error(f"数据库初始化失败: {str(e)}")

    def is_news_pushed(self, url):
        """检查新闻是否已推送过"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM news WHERE url = ?', (url,))
            result = cursor.fetchone()
            conn.close()
            return result is not None
        except Exception as e:
            logger.error(f"检查新闻失败: {str(e)}")
            return False

    def add_news(self, url, title, category, source):
        """添加新闻到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO news (url, title, category, source) VALUES (?, ?, ?, ?)',
                (url, title, category, source)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            logger.debug(f"新闻已存在: {url}")
            return False
        except Exception as e:
            logger.error(f"添加新闻失败: {str(e)}")
            return False

    def get_recent_news_count(self, hours=24):
        """获取最近N小时内推送的新闻数"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT COUNT(*) FROM news
                   WHERE push_time > datetime('now', '-' || ? || ' hours')''',
                (hours,)
            )
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            logger.error(f"查询新闻计数失败: {str(e)}")
            return 0

    def clear_old_data(self, days=30):
        """清理超过N天的旧数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                '''DELETE FROM news
                   WHERE push_time < datetime('now', '-' || ? || ' days')''',
                (days,)
            )
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            if deleted > 0:
                logger.info(f"清理了{deleted}条旧新闻数据")
            return True
        except Exception as e:
            logger.error(f"清理数据失败: {str(e)}")
            return False
