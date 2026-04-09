"""
邮件发送模块 - 支持双邮箱 + 分类 + HTML格式
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
        """发送新闻到配置的邮箱"""
        if not news_list:
            logger.warning("没有新闻需要发送")
            return False

        email_body = self._generate_email_body(news_list)

        success = True

        # 发送到第一个邮箱
        if not self._send_to_email(self.email, self.auth_code, email_body):
            success = False

        # 发送到第二个邮箱（如果配置了）
        if self.email2 and self.auth_code2:
            if not self._send_to_email(self.email2, self.auth_code2, email_body):
                success = False

        return success

    def _send_to_email(self, email, auth_code, email_body):
        """发送邮件到指定邮箱"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"{config.EMAIL_SUBJECT_PREFIX} {datetime.now().strftime('%Y年%m月%d日')}"
            msg['From'] = email
            msg['To'] = email

            part = MIMEText(email_body, 'plain', 'utf-8')
            msg.attach(part)

            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.login(email, auth_code)
                server.send_message(msg)

            logger.info(f"邮件成功发送到: {email}")
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error(f"认证失败: {email}")
            return False
        except Exception as e:
            logger.error(f"发送失败 ({email}): {str(e)}")
            return False

    def _generate_email_body(self, news_list):
        """生成分类邮件内容"""
        from summary_generator import categorize_news, get_professional_explanation, get_simple_explanation

        body = f"AI新闻日报 - {datetime.now().strftime('%Y年%m月%d日 %H:%M')}\n"
        body += "=" * 70 + "\n\n"

        # 按细致分类组织
        categories = defaultdict(list)
        for news in news_list:
            # 使用智能分类
            detailed_category = categorize_news(news.get('title', ''), news.get('summary', ''))
            categories[detailed_category].append(news)

        # 按分类输出
        for category in sorted(categories.keys()):
            items = categories[category]
            body += f"\n【{category}】({len(items)}条新闻)\n"
            body += "-" * 70 + "\n\n"

            for i, news in enumerate(items, 1):
                title = news.get('title', '标题缺失')
                summary = news.get('summary', '暂无摘要')[:100]
                url = news.get('url', '#')
                source = news.get('source', '未知来源')

                # 生成专业版和简洁版
                try:
                    pro_explain = get_professional_explanation(category, title, summary)[:150]
                    simple_explain = get_simple_explanation(category, title, summary)[:120]
                except:
                    pro_explain = summary[:100]
                    simple_explain = summary[:80]

                body += f"{i}. {title}\n"
                body += f"   来源: {source}\n"
                body += f"   摘要: {summary}\n"
                body += f"   【专业版】{pro_explain}\n"
                body += f"   【简洁版】{simple_explain}\n"
                body += f"   链接: {url}\n\n"

        body += "=" * 70 + "\n"
        body += "📊 统计信息:\n"
        body += f"   总计: {len(news_list)}条新闻\n"
        body += f"   分类: {len(categories)}个主题\n"
        body += "\n本邮件由AI新闻聚合系统自动生成\n"

        return body
