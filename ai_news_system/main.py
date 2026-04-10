"""
主程序入口 - AI新闻聚合推送系统（完整版）
包含：爬取 → 分类 → 报告生成 → 邮件推送
"""
import logging
import os
from datetime import datetime
import config
from ai_news_fetcher import NewsAggregator
from email_sender import EmailSender
from database import NewsDatabase
from summary_generator import categorize_news, get_professional_explanation, get_simple_explanation
from report_generator import ReportGenerator


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


def classify_and_enrich_news(news_list):
    """对新闻进行分类和增强（添加专业版和简洁版解读）"""
    classified_news = []

    for news in news_list:
        title = news.get('title', '')
        summary = news.get('summary', '')

        # 智能分类
        detailed_category = categorize_news(title, summary)

        # 生成专业版和简洁版解读
        try:
            professional = get_professional_explanation(detailed_category, title, summary)
            simple = get_simple_explanation(detailed_category, title, summary)
        except:
            professional = summary[:150]
            simple = summary[:100]

        # 增强新闻对象
        enriched_news = news.copy()
        enriched_news['category'] = detailed_category
        enriched_news['professional_explanation'] = professional
        enriched_news['simple_explanation'] = simple

        classified_news.append(enriched_news)

    return classified_news


def main():
    """主函数"""
    logger = setup_logging()

    logger.info("=" * 60)
    logger.info("AI新闻聚合推送系统 - 完整版启动")
    logger.info("=" * 60)

    try:
        # 步骤1：初始化数据库
        logger.info("[步骤1] 初始化数据库...")
        db = NewsDatabase(config.DB_PATH)

        # 步骤2：爬取新闻
        logger.info("[步骤2] 爬取新闻...")
        aggregator = NewsAggregator(db)
        news_list = aggregator.fetch_all_news()

        if not news_list:
            logger.warning("没有新闻可推送")
            return False

        logger.info(f"共爬取 {len(news_list)} 条新闻")

        # 步骤3：分类和增强
        logger.info("[步骤3] 分类和增强新闻...")
        classified_news = classify_and_enrich_news(news_list)

        # 步骤4：生成报告
        logger.info("[步骤4] 生成HTML报告...")
        report_gen = ReportGenerator()
        html_report = report_gen.generate_html_report(classified_news)

        # 保存HTML报告到本地（可选）
        try:
            reports_dir = os.path.join(config.LOG_DIR, 'reports')
            os.makedirs(reports_dir, exist_ok=True)
            report_path = os.path.join(reports_dir, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_report)
            logger.info(f"HTML报告已保存: {report_path}")
        except Exception as e:
            logger.warning(f"保存HTML报告失败: {str(e)}")

        # 步骤5：发送邮件
        logger.info("[步骤5] 发送邮件...")
        email_sender = EmailSender()
        success = email_sender.send_news(classified_news)

        if success:
            logger.info(f"新闻已推送到 {len(email_sender.emails)} 个邮箱")
            # 清理旧数据
            db.clear_old_data(days=30)
            logger.info("旧数据已清理")
        else:
            logger.error("新闻推送失败")
            return False

        logger.info("=" * 60)
        logger.info("程序执行完毕 ✓")
        logger.info("=" * 60)
        return True

    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}", exc_info=True)
        return False


if __name__ == '__main__':
    main()
