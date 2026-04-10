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
        """生成科技风中文HTML邮件 — 科学布局版"""
        from summary_generator import categorize_news

        # 按分类组织
        categories = defaultdict(list)
        for news in news_list:
            category = news.get('category', '其他')
            categories[category].append(news)

        # 分类配色
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

        # 来源标签颜色
        source_colors = {
            '机器之心': '#e91e63', '量子位': '#ff9800', 'AI前线': '#4caf50',
            'AI科技大本营': '#2196f3', '新智元': '#9c27b0',
            'Hacker News': '#ff6b6b', 'arXiv': '#42a5f5',
            'OpenAI Blog': '#00f0ff', 'OpenAI Research': '#00f0ff',
            'DeepMind Blog': '#7b2ff7', 'Anthropic': '#bb86fc',
            'Microsoft Research': '#0078d4', 'Nvidia Blog': '#76b900',
            'Stanford HAI': '#8c1515', 'MIT CSAIL': '#a31f34',
        }

        # 构建分类HTML
        categories_html = ""
        for category in sorted(categories.keys()):
            items = categories[category]
            color = color_map.get(category, '#78909c')

            categories_html += f'''
            <div class="cat-section">
                <div class="cat-header" style="display: flex; align-items: center; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.06);">
                    <span class="cat-dot" style="display: inline-block; width: 6px; height: 6px; background: {color}; border-radius: 50%; box-shadow: 0 0 8px {color}; margin-right: 10px;"></span>
                    <h3 style="color: {color}; margin: 0; font-size: 15px; font-weight: 600; letter-spacing: 0.5px;">{category}</h3>
                    <span class="cat-count" style="margin-left: auto; font-size: 12px; color: #546e7a; background: rgba(255,255,255,0.04); padding: 2px 8px; border-radius: 10px;">{len(items)} 条</span>
                </div>
            '''

            for i, news in enumerate(items[:6], 1):
                title = news.get('title', '标题缺失')
                source = news.get('source', '未知来源')
                url = news.get('url', '#')
                summary = news.get('summary', '暂无摘要')[:150]
                pro = news.get('professional_explanation', '')[:150]
                simple = news.get('simple_explanation', '')[:130]
                orig_title = news.get('original_title', '')

                src_color = source_colors.get(source, '#607d8b')

                # 翻译标记
                trans_badge = ''
                if orig_title:
                    trans_badge = f'<span style="font-size: 10px; color: #546e7a; background: rgba(255,255,255,0.04); padding: 1px 5px; border-radius: 2px; margin-left: 6px;">翻译</span>'

                categories_html += f'''
                <div class="news-item" style="padding: 14px 16px; background: rgba(255,255,255,0.02); border-radius: 8px; margin-bottom: 8px; border-left: 3px solid {color}; display: flex; gap: 14px; align-items: flex-start;">
                    <div class="num" style="min-width: 28px; height: 28px; background: rgba(255,255,255,0.04); color: {color}; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700;">{i}</div>
                    <div style="flex: 1; min-width: 0;">
                        <div class="title-row" style="display: flex; align-items: baseline; gap: 8px; margin-bottom: 4px; flex-wrap: wrap;">
                            <a href="{url}" target="_blank" style="color: #e8eaed; font-size: 14px; font-weight: 500; text-decoration: none; word-break: break-word;">{title}</a>
                            {trans_badge}
                        </div>
                        <div class="meta-row" style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px; flex-wrap: wrap;">
                            <span class="source-tag" style="font-size: 10px; color: {src_color}; background: rgba(255,255,255,0.04); padding: 1px 6px; border-radius: 3px; font-weight: 500;">{source}</span>
                        </div>
                        <div class="summary" style="font-size: 12px; color: #9e9e9e; line-height: 1.6; margin-bottom: 8px;">{summary}</div>
                        {self._render_explanations(pro, simple)}
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
        body {{ background: #0d1117; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', 'PingFang SC', sans-serif; color: #c9d1d9; margin: 0; padding: 16px; line-height: 1.5; }}
        .wrap {{ max-width: 720px; margin: 0 auto; background: #161b22; border-radius: 12px; overflow: hidden; border: 1px solid #21262d; }}

        /* Header */
        .header {{ padding: 32px 24px 24px; text-align: center; background: linear-gradient(180deg, #0d1117 0%, #161b22 100%); border-bottom: 1px solid #21262d; }}
        .header h1 {{ font-size: 28px; font-weight: 700; color: #f0f6fc; margin: 0 0 8px 0; letter-spacing: 1.5px; }}
        .header .line {{ width: 48px; height: 2px; background: linear-gradient(90deg, #58a6ff, #bc8cff); margin: 0 auto 10px; border-radius: 1px; }}
        .header .date {{ font-size: 13px; color: #8b949e; margin: 0 0 8px; }}
        .header .pill {{ display: inline-block; font-size: 11px; color: #58a6ff; background: rgba(56,139,253,0.08); padding: 3px 12px; border-radius: 12px; border: 1px solid rgba(56,139,253,0.2); }}

        /* Stats */
        .stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1px; background: #21262d; border-bottom: 1px solid #21262d; }}
        .stat {{ background: #161b22; padding: 16px 12px; text-align: center; }}
        .stat-val {{ font-size: 24px; font-weight: 700; color: #58a6ff; }}
        .stat-lbl {{ font-size: 11px; color: #8b949e; margin-top: 2px; text-transform: uppercase; letter-spacing: 0.5px; }}

        /* Content */
        .content {{ padding: 20px 20px 8px; }}
        .cat-section {{ margin-bottom: 24px; }}

        /* Footer */
        .footer {{ text-align: center; padding: 16px 24px; border-top: 1px solid #21262d; background: #0d1117; }}
        .footer .badges {{ margin-bottom: 6px; }}
        .footer .badge {{ display: inline-block; font-size: 10px; color: #8b949e; background: rgba(255,255,255,0.04); padding: 2px 7px; border-radius: 3px; margin: 2px; }}
        .footer .copy {{ font-size: 11px; color: #484f58; margin: 4px 0 0; }}

        @media (max-width: 600px) {{
            body {{ padding: 8px; }}
            .stats {{ grid-template-columns: 1fr; }}
            .wrap {{ border-radius: 8px; }}
            .content {{ padding: 16px 12px 8px; }}
            .news-item {{ flex-direction: column; gap: 8px; }}
            .explain-grid {{ grid-template-columns: 1fr !important; }}
        }}
    </style>
</head>
<body>
    <div class="wrap">
        <div class="header">
            <h1>AI NEWS</h1>
            <div class="line"></div>
            <p class="date">{today} · {week_day}</p>
            <span class="pill">全球 AI 资讯聚合 · 每日更新</span>
        </div>
        <div class="stats">
            <div class="stat">
                <div class="stat-val">{total_news}</div>
                <div class="stat-lbl">新闻</div>
            </div>
            <div class="stat">
                <div class="stat-val">{total_cats}</div>
                <div class="stat-lbl">分类</div>
            </div>
            <div class="stat">
                <div class="stat-val">{total_sources}</div>
                <div class="stat-lbl">来源</div>
            </div>
        </div>
        <div class="content">
            {categories_html}
        </div>
        <div class="footer">
            <div class="badges">
                <span class="badge">智能分类</span>
                <span class="badge">双语解读</span>
                <span class="badge">自动去重</span>
                <span class="badge">每日 08:00</span>
            </div>
            <p class="copy">AI 新闻聚合系统 · 自动生成</p>
        </div>
    </div>
</body>
</html>'''

        return html

    def _render_explanations(self, pro, simple):
        """渲染专业/简洁解读"""
        if not pro and not simple:
            return ''
        return f'''
        <div class="explain-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px;">
            <div style="background: rgba(56,139,253,0.06); padding: 6px 10px; border-radius: 6px; border-left: 2px solid rgba(56,139,253,0.4);">
                <span style="color: #58a6ff; font-size: 10px; font-weight: 600;">专业</span>
                <span style="color: #8b949e; font-size: 11px;"> {pro}</span>
            </div>
            <div style="background: rgba(188,140,255,0.06); padding: 6px 10px; border-radius: 6px; border-left: 2px solid rgba(188,140,255,0.4);">
                <span style="color: #bc8cff; font-size: 10px; font-weight: 600;">简洁</span>
                <span style="color: #8b949e; font-size: 11px;"> {simple}</span>
            </div>
        </div>
        '''

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
