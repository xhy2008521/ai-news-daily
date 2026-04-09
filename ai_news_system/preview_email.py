"""
本地邮件预览工具 - 在发送前查看HTML效果
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
from datetime import datetime
from ai_news_fetcher import NewsAggregator
from database import NewsDatabase
from summary_generator import categorize_news, get_professional_explanation, get_simple_explanation
from email_sender import EmailSender
import config

def preview_email():
    """生成并预览邮件"""
    print("\n" + "="*80)
    print("邮件预览工具 - HTML版本")
    print("="*80 + "\n")

    try:
        # 获取最新新闻
        print("[步骤1] 加载数据库和新闻...")
        db = NewsDatabase(config.DB_PATH)
        aggregator = NewsAggregator(db)
        news_list = aggregator.fetch_all_news()

        if not news_list:
            print("✗ 没有新闻可预览")
            return

        print(f"✓ 加载 {len(news_list)} 条新闻\n")

        # 分类和增强
        print("[步骤2] 分类和增强新闻...")
        classified_news = []
        for news in news_list:
            title = news.get('title', '')
            summary = news.get('summary', '')

            detailed_category = categorize_news(title, summary)

            try:
                professional = get_professional_explanation(detailed_category, title, summary)
                simple = get_simple_explanation(detailed_category, title, summary)
            except:
                professional = summary[:150]
                simple = summary[:100]

            enriched_news = news.copy()
            enriched_news['category'] = detailed_category
            enriched_news['professional_explanation'] = professional
            enriched_news['simple_explanation'] = simple

            classified_news.append(enriched_news)

        print(f"✓ 分类完成\n")

        # 生成HTML
        print("[步骤3] 生成HTML邮件...")
        sender = EmailSender()
        html_body = sender._generate_html_email(classified_news)

        # 保存到本地
        preview_path = os.path.join(config.LOG_DIR, 'email_preview.html')
        os.makedirs(config.LOG_DIR, exist_ok=True)

        with open(preview_path, 'w', encoding='utf-8') as f:
            f.write(html_body)

        print(f"✓ HTML已生成\n")

        # 显示信息
        print("="*80)
        print("📧 邮件预览信息")
        print("="*80)
        print(f"文件位置: {preview_path}")
        print(f"文件大小: {len(html_body)/1024:.1f} KB")
        print(f"新闻数量: {len(classified_news)}")
        print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n✓ 请用浏览器打开预览文件查看最终效果")
        print("="*80 + "\n")

        # 统计分类
        from collections import defaultdict
        categories = defaultdict(int)
        sources = defaultdict(int)

        for news in classified_news:
            categories[news.get('category', '其他')] += 1
            sources[news.get('source', '未知')] += 1

        print("📊 新闻分布:")
        print("\n【按分类】:")
        for cat in sorted(categories.keys()):
            print(f"  {cat}: {categories[cat]}条")

        print("\n【按来源（TOP 10）】:")
        sorted_sources = sorted(sources.items(), key=lambda x: x[1], reverse=True)
        for source, count in sorted_sources[:10]:
            print(f"  {source}: {count}条")

        print("\n" + "="*80)

    except Exception as e:
        print(f"✗ 预览失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    preview_email()
