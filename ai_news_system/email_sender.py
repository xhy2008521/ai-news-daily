"""
邮件发送模块 - 完整版（HTML + 纯文本双格式 + 分类 + 解读）
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from collections import defaultdict
import config
import logging

logger = logging.getLogger(__name__)


class EmailSender:
    def __init__(self):
        self.smtp_server = config.SMTP_SERVER
        self.smtp_port = config.SMTP_PORT
        self.email = config.QQ_EMAIL
        self.auth_code = config.QQ_AUTH_CODE
        self.email2 = getattr(config, 'QQ_EMAIL2', None)
        self.auth_code2 = getattr(config, 'QQ_AUTH_CODE2', None)

    def send_news(self, news_list):
        """发送新闻到配置的邮箱（HTML + 纯文本）"""
        if not news_list:
            logger.warning("没有新闻需要发送")
            return False

        # 生成两个版本
        html_body = self._generate_html_email(news_list)
        text_body = self._generate_text_email(news_list)

        success = True

        # 发送到第一个邮箱
        if not self._send_to_email(self.email, self.auth_code, html_body, text_body):
            success = False

        # 发送到第二个邮箱（如果配置了）
        if self.email2 and self.auth_code2:
            if not self._send_to_email(self.email2, self.auth_code2, html_body, text_body):
                success = False

        return success

    def _send_to_email(self, email, auth_code, html_body, text_body):
        """发送邮件到指定邮箱（同时支持HTML和纯文本）"""
        try:
            # 创建多部分邮件（HTML优先，纯文本备用）
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"{config.EMAIL_SUBJECT_PREFIX} {datetime.now().strftime('%Y年%m月%d日')}"
            msg['From'] = email
            msg['To'] = email

            # 先添加纯文本部分（备用）
            text_part = MIMEText(text_body, 'plain', 'utf-8')
            msg.attach(text_part)

            # 再添加HTML部分（优先显示）
            html_part = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(html_part)

            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.login(email, auth_code)
                server.send_message(msg)

            logger.info(f"邮件成功发送到: {email} (HTML + 纯文本)")
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error(f"认证失败: {email}")
            return False
        except Exception as e:
            logger.error(f"发送失败 ({email}): {str(e)}")
            return False

    def _generate_html_email(self, news_list):
        """生成美观的HTML邮件"""
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
                    📌 {category} ({len(items)}条)
                </h3>
            '''

            for i, news in enumerate(items[:6], 1):  # 每个分类最多显示6条
                title = news.get('title', '标题缺失')
                source = news.get('source', '未知来源')
                url = news.get('url', '#')
                summary = news.get('summary', '暂无摘要')[:100]
                pro = news.get('professional_explanation', '')[:120]
                simple = news.get('simple_explanation', '')[:100]

                categories_html += f'''
                <div class="news-card">
                    <div class="news-number" style="background-color: {color};">{i}</div>
                    <div class="news-content">
                        <div class="news-title">
                            <a href="{url}" target="_blank" style="color: {color};">{title}</a>
                        </div>
                        <div class="news-source">📍 {source}</div>
                        <div class="news-summary">{summary}</div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 8px; font-size: 12px;">
                            <div style="background: #f0f0f0; padding: 8px; border-radius: 4px;">
                                <strong style="color: #5e72e4;">专业版:</strong> {pro}
                            </div>
                            <div style="background: #f9f9f9; padding: 8px; border-radius: 4px;">
                                <strong style="color: #764ba2;">简洁版:</strong> {simple}
                            </div>
                        </div>
                    </div>
                </div>
                '''

            categories_html += '</div>'

        html = f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI新闻日报</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif;
            background: #f5f7fa;
            color: #333;
            line-height: 1.6;
            padding: 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 50px 30px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 36px;
            margin-bottom: 10px;
            letter-spacing: 1px;
        }}
        .header p {{
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 20px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            padding: 0 30px;
            margin-top: -30px;
            position: relative;
            z-index: 1;
        }}
        .stat {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        .stat-value {{
            font-size: 28px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        .stat-label {{
            font-size: 12px;
            color: #666;
        }}
        .content {{
            padding: 30px;
        }}
        .category-section {{
            margin-bottom: 25px;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 8px;
        }}
        .news-card {{
            display: flex;
            gap: 15px;
            padding: 15px;
            background: white;
            border-radius: 6px;
            margin-bottom: 12px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }}
        .news-card:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        .news-number {{
            display: flex;
            align-items: center;
            justify-content: center;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            color: white;
            font-weight: bold;
            flex-shrink: 0;
        }}
        .news-content {{
            flex: 1;
        }}
        .news-title {{
            font-size: 15px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .news-title a {{
            text-decoration: none;
        }}
        .news-title a:hover {{
            text-decoration: underline;
        }}
        .news-source {{
            font-size: 12px;
            color: #999;
            margin-bottom: 5px;
        }}
        .news-summary {{
            font-size: 13px;
            color: #666;
            margin-bottom: 8px;
            line-height: 1.5;
        }}
        .footer {{
            background: #f5f7fa;
            padding: 20px 30px;
            text-align: center;
            font-size: 12px;
            color: #999;
            border-top: 1px solid #e0e0e0;
        }}
        .footer p {{
            margin: 5px 0;
        }}
        @media (max-width: 600px) {{
            .stats {{
                grid-template-columns: 1fr;
            }}
            .news-card {{
                flex-direction: column;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI新闻日报</h1>
            <p>优质内容聚合 • 智能分类解读 • 专业 + 简洁双版本</p>
            <p>{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
        </div>

        <div class="stats">
            <div class="stat">
                <div class="stat-value">{len(news_list)}</div>
                <div class="stat-label">条新闻</div>
            </div>
            <div class="stat">
                <div class="stat-value">{len(categories)}</div>
                <div class="stat-label">个分类</div>
            </div>
            <div class="stat">
                <div class="stat-value">{len(set(n.get('source', '') for n in news_list))}</div>
                <div class="stat-label">个来源</div>
            </div>
        </div>

        <div class="content">
            {categories_html}
        </div>

        <div class="footer">
            <p><strong>📊 关键特性</strong></p>
            <p>✓ 9类专业分类  ✓ 专业版+简洁版双解读  ✓ 22个优质信息源</p>
            <p>✓ 自动去重  ✓ 每日早8:00自动推送  ✓ 支持多邮箱接收</p>
            <p style="margin-top: 15px; color: #ccc;">本邮件由AI新闻聚合系统自动生成 • 系统已配置到GitHub Actions自动化</p>
        </div>
    </div>
</body>
</html>
        '''

        return html

    def _generate_text_email(self, news_list):
        """生成纯文本版本（备用）"""
        from summary_generator import categorize_news

        body = f"AI新闻日报 - {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n"
        body += "=" * 80 + "\n\n"

        # 按分类组织
        categories = defaultdict(list)
        for news in news_list:
            category = news.get('category', '其他')
            categories[category].append(news)

        # 按分类输出
        for category in sorted(categories.keys()):
            items = categories[category]
            body += f"\n【{category}】({len(items)}条新闻)\n"
            body += "-" * 80 + "\n\n"

            for i, news in enumerate(items, 1):
                title = news.get('title', '标题缺失')
                summary = news.get('summary', '暂无摘要')[:100]
                url = news.get('url', '#')
                source = news.get('source', '未知来源')
                pro = news.get('professional_explanation', '')[:150]
                simple = news.get('simple_explanation', '')[:120]

                body += f"{i}. {title}\n"
                body += f"   来源: {source}\n"
                body += f"   摘要: {summary}\n"
                body += f"   【专业版】{pro}\n"
                body += f"   【简洁版】{simple}\n"
                body += f"   链接: {url}\n\n"

        body += "=" * 80 + "\n"
        body += "📊 统计信息:\n"
        body += f"   总计: {len(news_list)}条新闻\n"
        body += f"   分类: {len(categories)}个主题\n"
        body += f"   来源: {len(set(n.get('source', '') for n in news_list))}个\n"
        body += "\n" + "=" * 80 + "\n"
        body += "✓ 系统特性:\n"
        body += "   • 9类专业分类 (大模型突破、推理能力、长上下文、多模态等)\n"
        body += "   • 专业版+简洁版双解读\n"
        body += "   • 22个优质信息源\n"
        body += "   • 自动去重和重排序\n"
        body += "   • 每日早8:00自动推送\n"
        body += "   • 支持多邮箱接收\n"
        body += "\n本邮件由AI新闻聚合系统自动生成\n"

        return body
