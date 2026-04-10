"""
邮件发送模块 - 全中文版（HTML + 纯文本双格式 + 分类 + 解读 + 动态多邮箱）
"""
import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from collections import defaultdict
import config

logger = logging.getLogger(__name__)


def _get_all_emails():
    """动态获取 config.py 中所有已配置的邮箱（不限数量）"""
    emails = []
    # 获取第一个邮箱
    email = getattr(config, 'QQ_EMAIL', None)
    auth = getattr(config, 'QQ_AUTH_CODE', None)
    if email and auth:
        emails.append((email, auth))

    # 获取第2~N个邮箱
    for i in range(2, 20):  # 最多支持19个额外邮箱
        email = getattr(config, f'QQ_EMAIL{i}', None)
        auth = getattr(config, f'QQ_AUTH_CODE{i}', None)
        if email and auth:
            emails.append((email, auth))

    return emails


class EmailSender:
    def __init__(self):
        self.smtp_server = config.SMTP_SERVER
        self.smtp_port = config.SMTP_PORT
        self.emails = _get_all_emails()

    def send_news(self, news_list):
        """发送新闻到所有配置的邮箱"""
        if not news_list:
            logger.warning("没有新闻需要发送")
            return False

        if not self.emails:
            logger.error("没有配置任何邮箱")
            return False

        # 生成两个版本
        html_body = self._generate_html_email(news_list)
        text_body = self._generate_text_email(news_list)

        success_count = 0
        for email, auth_code in self.emails:
            if self._send_to_email(email, auth_code, html_body, text_body):
                success_count += 1

        total = len(self.emails)
        if success_count == total:
            logger.info(f"邮件已成功推送到全部 {total} 个邮箱")
        else:
            logger.warning(f"邮件推送: {success_count}/{total} 成功")

        return success_count > 0

    def _send_to_email(self, email, auth_code, html_body, text_body):
        """发送邮件到指定邮箱（HTML + 纯文本双格式）"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"AI新闻日报 | {datetime.now().strftime('%Y年%m月%d日')}"
            msg['From'] = email
            msg['To'] = email

            # 纯文本备用
            text_part = MIMEText(text_body, 'plain', 'utf-8')
            msg.attach(text_part)

            # HTML 优先
            html_part = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(html_part)

            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=15) as server:
                server.login(email, auth_code)
                server.send_message(msg)

            logger.info(f"邮件成功发送到: {email}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"认证失败 ({email}): {e}")
            return False
        except Exception as e:
            logger.error(f"发送失败 ({email}): {e}")
            return False

    def _generate_html_email(self, news_list):
        """生成全中文美观的HTML邮件"""
        from summary_generator import categorize_news

        # 按分类组织
        categories = defaultdict(list)
        for news in news_list:
            category = news.get('category', '其他')
            categories[category].append(news)

        # 颜色映射
        color_map = {
            '大模型突破': '#FF6B6B',
            '推理能力': '#4ECDC4',
            '长上下文': '#45B7D1',
            '多模态': '#FFA07A',
            '开源': '#98D8C8',
            '应用产品': '#F7DC6F',
            '优化效率': '#BB8FCE',
            '安全治理': '#F8B88B',
            '论文研究': '#85C1E2',
            '其他': '#95A5A6'
        }

        # 构建分类HTML
        categories_html = ""
        for category in sorted(categories.keys()):
            items = categories[category]
            color = color_map.get(category, '#95A5A6')

            categories_html += f'''
            <div class="category-section" style="border-left: 5px solid {color};">
                <h3 style="color: {color}; margin: 15px 0 10px 0; padding-left: 10px;">
                    {category}（{len(items)}条）
                </h3>
            '''

            for i, news in enumerate(items[:6], 1):  # 每类最多6条
                title = news.get('title', '标题缺失')
                source = news.get('source', '未知来源')
                url = news.get('url', '#')
                summary = news.get('summary', '暂无摘要')[:120]
                pro = news.get('professional_explanation', '')[:130]
                simple = news.get('simple_explanation', '')[:110]

                categories_html += f'''
                <div class="news-card">
                    <div class="news-number" style="background-color: {color};">{i}</div>
                    <div class="news-content">
                        <div class="news-title">
                            <a href="{url}" target="_blank" style="color: {color};">{title}</a>
                        </div>
                        <div class="news-source">来源: {source}</div>
                        <div class="news-summary">{summary}</div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 8px; font-size: 12px;">
                            <div style="background: #f0f4ff; padding: 8px; border-radius: 4px;">
                                <strong style="color: #5e72e4;">专业解读:</strong> {pro}
                            </div>
                            <div style="background: #f9f5ff; padding: 8px; border-radius: 4px;">
                                <strong style="color: #764ba2;">简洁解读:</strong> {simple}
                            </div>
                        </div>
                    </div>
                </div>
                '''

            categories_html += '</div>'

        # 统计信息
        total_news = len(news_list)
        total_cats = len(categories)
        total_sources = len(set(n.get('source', '') for n in news_list))

        today = datetime.now().strftime('%Y年%m月%d日')

        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI新闻日报</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', 'PingFang SC', sans-serif;
            background: #f0f2f5;
            color: #333;
            line-height: 1.6;
            padding: 20px;
        }}
        .container {{
            max-width: 860px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px 30px;
            text-align: center;
        }}
        .header h1 {{ font-size: 32px; margin-bottom: 8px; letter-spacing: 1px; }}
        .header .subtitle {{ font-size: 14px; opacity: 0.9; margin-bottom: 6px; }}
        .header .date {{ font-size: 13px; opacity: 0.8; }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            padding: 0 25px;
            margin-top: -25px;
            position: relative;
            z-index: 1;
        }}
        .stat {{
            background: white;
            padding: 18px 12px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        .stat-value {{ font-size: 26px; font-weight: bold; color: #667eea; margin-bottom: 4px; }}
        .stat-label {{ font-size: 12px; color: #888; }}
        .content {{ padding: 25px; }}
        .category-section {{
            margin-bottom: 22px;
            padding: 14px;
            background: #fafbfc;
            border-radius: 8px;
        }}
        .news-card {{
            display: flex;
            gap: 12px;
            padding: 14px;
            background: white;
            border-radius: 6px;
            margin-bottom: 10px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        }}
        .news-number {{
            display: flex;
            align-items: center;
            justify-content: center;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            color: white;
            font-weight: bold;
            flex-shrink: 0;
            font-size: 14px;
        }}
        .news-content {{ flex: 1; min-width: 0; }}
        .news-title {{ font-size: 14px; font-weight: bold; margin-bottom: 4px; }}
        .news-title a {{ text-decoration: none; word-break: break-word; }}
        .news-title a:hover {{ text-decoration: underline; }}
        .news-source {{ font-size: 12px; color: #999; margin-bottom: 4px; }}
        .news-summary {{ font-size: 13px; color: #555; margin-bottom: 6px; line-height: 1.5; }}
        .footer {{
            background: #f8f9fa;
            padding: 20px 25px;
            text-align: center;
            font-size: 12px;
            color: #999;
            border-top: 1px solid #eee;
        }}
        .footer .features {{ margin-bottom: 8px; }}
        .footer .features span {{ display: inline-block; margin: 2px 6px; color: #667eea; }}
        @media (max-width: 600px) {{
            .stats {{ grid-template-columns: 1fr; }}
            .news-card {{ flex-direction: column; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AI 新闻日报</h1>
            <p class="subtitle">智能分类解读 | 专业 + 简洁双版本</p>
            <p class="date">{today}</p>
        </div>
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{total_news}</div>
                <div class="stat-label">条新闻</div>
            </div>
            <div class="stat">
                <div class="stat-value">{total_cats}</div>
                <div class="stat-label">个分类</div>
            </div>
            <div class="stat">
                <div class="stat-value">{total_sources}</div>
                <div class="stat-label">个来源</div>
            </div>
        </div>
        <div class="content">
            {categories_html}
        </div>
        <div class="footer">
            <p class="features">
                <span>智能分类</span> | <span>双版本解读</span> | <span>自动去重</span> | <span>每日推送</span>
            </p>
            <p>本邮件由 AI 新闻聚合系统自动生成发送</p>
        </div>
    </div>
</body>
</html>'''

        return html

    def _generate_text_email(self, news_list):
        """生成纯中文文本版本（备用）"""
        from summary_generator import categorize_news

        today = datetime.now().strftime('%Y年%m月%d日 %H:%M')
        body = f"AI 新闻日报 — {today}\n"
        body += "=" * 70 + "\n\n"

        categories = defaultdict(list)
        for news in news_list:
            category = news.get('category', '其他')
            categories[category].append(news)

        body += f"共 {len(news_list)} 条新闻，{len(categories)} 个分类，{len(set(n.get('source', '') for n in news_list))} 个来源\n\n"

        for category in sorted(categories.keys()):
            items = categories[category]
            body += f"【{category}】（{len(items)}条）\n"
            body += "-" * 70 + "\n\n"

            for i, news in enumerate(items, 1):
                title = news.get('title', '标题缺失')
                source = news.get('source', '未知来源')
                url = news.get('url', '#')
                summary = news.get('summary', '暂无摘要')[:120]
                pro = news.get('professional_explanation', '')[:150]
                simple = news.get('simple_explanation', '')[:120]

                body += f"{i}. {title}\n"
                body += f"   来源: {source}\n"
                body += f"   摘要: {summary}\n"
                if pro:
                    body += f"   专业解读: {pro}\n"
                if simple:
                    body += f"   简洁解读: {simple}\n"
                body += f"   链接: {url}\n\n"

        body += "=" * 70 + "\n"
        body += "本邮件由 AI 新闻聚合系统自动生成\n"

        return body
