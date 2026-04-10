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
            msg['Subject'] = f"AI NEWS | {datetime.now().strftime('%Y.%m.%d')} | 全球资讯聚合"
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
        """生成科技风中文HTML邮件"""
        from summary_generator import categorize_news

        # 按分类组织
        categories = defaultdict(list)
        for news in news_list:
            category = news.get('category', '其他')
            categories[category].append(news)

        # 分类配色（科技霓虹色）
        color_map = {
            '大模型突破': '#00f0ff',
            '推理能力': '#7b2ff7',
            '长上下文': '#00d4ff',
            '多模态': '#ff6b6b',
            '开源': '#00ff88',
            '应用产品': '#ffa726',
            '优化效率': '#bb86fc',
            '安全治理': '#ff7043',
            '论文研究': '#42a5f5',
            '其他': '#78909c'
        }

        # 构建分类HTML
        categories_html = ""
        for category in sorted(categories.keys()):
            items = categories[category]
            color = color_map.get(category, '#78909c')

            categories_html += f'''
            <div class="category-section" style="border-top: 2px solid {color}; margin-bottom: 24px; padding: 16px; background: rgba(255,255,255,0.02); border-radius: 8px;">
                <h3 style="color: {color}; margin: 0 0 14px 0; font-size: 16px; font-weight: 600; letter-spacing: 1px;">
                    <span style="display: inline-block; width: 8px; height: 8px; background: {color}; border-radius: 50%; margin-right: 8px; vertical-align: middle; box-shadow: 0 0 6px {color};"></span>
                    {category} <span style="font-size: 13px; opacity: 0.6; font-weight: 400;">({len(items)}条)</span>
                </h3>
            '''

            for i, news in enumerate(items[:6], 1):  # 每类最多6条
                title = news.get('title', '标题缺失')
                source = news.get('source', '未知来源')
                url = news.get('url', '#')
                summary = news.get('summary', '暂无摘要')[:140]
                pro = news.get('professional_explanation', '')[:140]
                simple = news.get('simple_explanation', '')[:120]
                orig_title = news.get('original_title', '')

                # 来源标签颜色
                source_colors = {
                    '机器之心': '#e91e63', '量子位': '#ff9800', 'AI前线': '#4caf50',
                    'Hacker News': '#ff6b6b', 'arXiv': '#42a5f5', 'OpenAI Blog': '#00f0ff',
                    'DeepMind Blog': '#7b2ff7', 'Anthropic': '#bb86fc',
                }
                src_color = source_colors.get(source, '#607d8b')

                # 如果有原文标题，显示翻译对比
                orig_html = ""
                if orig_title:
                    orig_html = f'<div style="font-size: 11px; color: #78909c; margin-bottom: 4px; font-style: italic;">原文: {orig_title}</div>'

                categories_html += f'''
                <div class="news-card" style="display: flex; gap: 12px; padding: 14px; background: rgba(255,255,255,0.03); border-radius: 6px; margin-bottom: 10px; border-left: 3px solid {color};">
                    <div style="min-width: 32px; height: 32px; background: rgba(0,240,255,0.1); color: {color}; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 13px;">{i}</div>
                    <div style="flex: 1; min-width: 0;">
                        <div style="margin-bottom: 2px;">{orig_html}<a href="{url}" target="_blank" style="color: #e0e0e0; font-size: 14px; font-weight: 500; text-decoration: none;">{title}</a></div>
                        <div style="margin-bottom: 4px;">
                            <span style="font-size: 11px; color: {src_color}; background: rgba(255,255,255,0.06); padding: 2px 6px; border-radius: 3px;">{source}</span>
                        </div>
                        <div style="font-size: 12px; color: #9e9e9e; line-height: 1.5; margin-bottom: 6px;">{summary}</div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 11px;">
                            <div style="background: rgba(0,240,255,0.04); padding: 6px 8px; border-radius: 4px; border-left: 2px solid rgba(0,240,255,0.3);">
                                <span style="color: #00f0ff; font-weight: 500;">专业:</span> <span style="color: #b0bec5;">{pro}</span>
                            </div>
                            <div style="background: rgba(123,47,247,0.04); padding: 6px 8px; border-radius: 4px; border-left: 2px solid rgba(123,47,247,0.3);">
                                <span style="color: #bb86fc; font-weight: 500;">简洁:</span> <span style="color: #b0bec5;">{simple}</span>
                            </div>
                        </div>
                    </div>
                </div>
                '''

            categories_html += '</div>'

        # 统计
        total_news = len(news_list)
        total_cats = len(categories)
        total_sources = len(set(n.get('source', '') for n in news_list))
        today = datetime.now().strftime('%Y.%m.%d')
        week_day = datetime.now().strftime('%A')

        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 新闻日报</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        body {{ background: #0a0e17; font-family: 'Inter', -apple-system, 'Microsoft YaHei', sans-serif; color: #e0e0e0; margin: 0; padding: 0; }}
        .container {{ max-width: 800px; margin: 0 auto; background: #0f1623; }}
        .header {{ background: linear-gradient(135deg, #0a0e17 0%, #1a1f35 50%, #0f1623 100%); padding: 40px 30px 24px; text-align: center; border-bottom: 1px solid rgba(0,240,255,0.15); }}
        .header h1 {{ font-size: 32px; font-weight: 700; color: #ffffff; margin: 0 0 6px 0; letter-spacing: 2px; text-shadow: 0 0 20px rgba(0,240,255,0.3); }}
        .header .accent-line {{ width: 60px; height: 2px; background: linear-gradient(90deg, #00f0ff, #7b2ff7); margin: 0 auto 12px; border-radius: 1px; }}
        .header .date {{ font-size: 13px; color: #78909c; margin: 0; }}
        .header .tag {{ display: inline-block; font-size: 11px; color: #00f0ff; background: rgba(0,240,255,0.08); padding: 3px 10px; border-radius: 20px; margin-top: 10px; border: 1px solid rgba(0,240,255,0.2); }}
        .stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; padding: 20px 24px; }}
        .stat {{ background: rgba(0,240,255,0.03); padding: 16px 12px; border-radius: 8px; text-align: center; border: 1px solid rgba(0,240,255,0.08); }}
        .stat-value {{ font-size: 28px; font-weight: 700; color: #00f0ff; text-shadow: 0 0 10px rgba(0,240,255,0.2); }}
        .stat-label {{ font-size: 11px; color: #78909c; margin-top: 4px; text-transform: uppercase; letter-spacing: 1px; }}
        .content {{ padding: 0 24px 24px; }}
        .footer {{ text-align: center; padding: 20px 24px; border-top: 1px solid rgba(255,255,255,0.05); background: rgba(0,0,0,0.2); }}
        .footer .badges {{ margin-bottom: 8px; }}
        .footer .badge {{ display: inline-block; font-size: 10px; color: #78909c; background: rgba(255,255,255,0.04); padding: 3px 8px; border-radius: 3px; margin: 2px 3px; }}
        .footer .copyright {{ font-size: 11px; color: #455a64; margin: 6px 0 0; }}
        @media (max-width: 600px) {{ .stats {{ grid-template-columns: 1fr; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AI NEWS DAILY</h1>
            <div class="accent-line"></div>
            <p class="date">{today} | {week_day} | 全球 AI 资讯聚合</p>
            <span class="tag">智能分类 | 双语解读 | 每日更新</span>
        </div>
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{total_news}</div>
                <div class="stat-label">新闻</div>
            </div>
            <div class="stat">
                <div class="stat-value">{total_cats}</div>
                <div class="stat-label">分类</div>
            </div>
            <div class="stat">
                <div class="stat-value">{total_sources}</div>
                <div class="stat-label">来源</div>
            </div>
        </div>
        <div class="content">
            {categories_html}
        </div>
        <div class="footer">
            <div class="badges">
                <span class="badge">AI 驱动分类</span>
                <span class="badge">自动翻译</span>
                <span class="badge">去重过滤</span>
                <span class="badge">每日 08:00 推送</span>
            </div>
            <p class="copyright">本邮件由 AI 新闻聚合系统自动生成</p>
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
