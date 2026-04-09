"""
主程序入口 - AI新闻聚合推送系统
"""
import logging
import os
from datetime import datetime
import config
from ai_news_fetcher import NewsAggregator
from email_sender import EmailSender
from database import NewsDatabase


def setup_logging():
    """配置日志"""
    os.makedirs(config.LOG_DIR, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def main():
    """主函数"""
    logger = setup_logging()

    logger.info("=" * 60)
    logger.info("AI新闻聚合推送系统启动")
    logger.info("=" * 60)

    try:
        # 初始化数据库
        db = NewsDatabase(config.DB_PATH)

        # 爬取新闻
        aggregator = NewsAggregator(db)
        news_list = aggregator.fetch_all_news()

        # 过滤和排序
        news_list = sorted(news_list, key=lambda x: x.get('source', ''), reverse=True)

        if not news_list:
            logger.warning("没有新闻可推送")
            return False

        # 发送邮件
        email_sender = EmailSender()
        success = email_sender.send_news(news_list)

        if success:
            logger.info("新闻推送完成")
            # 清理旧数据
            db.clear_old_data(days=30)
        else:
            logger.error("新闻推送失败")
            return False

        logger.info("=" * 60)
        logger.info("程序执行完毕")
        logger.info("=" * 60)
        return True

    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}", exc_info=True)
        return False


if __name__ == '__main__':
    main()
