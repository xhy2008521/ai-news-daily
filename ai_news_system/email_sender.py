"""
邮件发送模块
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import config
import logging

logger = logging.getLogger(__name__)


class EmailSender:
    def __init__(self):
        self.smtp_server = config.SMTP_SERVER
        self.smtp_port = config.SMTP_PORT
        self.email = config.QQ_EMAIL
        self.auth_code = config.QQ_AUTH_CODE

    def send_news(self, news_list):
        """
        发送新闻邮件

        Args:
            news_list (list): 新闻列表，每条新闻是一个字典
                {
                    'category': '国内/国际/论文/官方',
                    'title': '新闻标题',
                    'summary': '一句摘要',
                    'url': '链接',
                    'source': '来源'
                }
        """
        try:
            if not news_list:
                logger.warning("没有新闻需要发送")
                return False

            # 生成邮件内容
            email_body = self._generate_email_body(news_list)

            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"{config.EMAIL_SUBJECT_PREFIX} {datetime.now().strftime('%Y年%m月%d日')}"
            msg['From'] = self.email
            msg['To'] = config.EMAIL_TO

            # 添加纯文本版本
            part = MIMEText(email_body, 'plain', 'utf-8')
            msg.attach(part)

            # 连接SMTP服务器并发送
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.login(self.email, self.auth_code)
                server.send_message(msg)

            logger.info(f"邮件发送成功！共{len(news_list)}条新闻")
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error("邮箱认证失败，请检查授权码是否正确")
            return False
        except Exception as e:
            logger.error(f"邮件发送失败: {str(e)}")
            return False

    def _generate_email_body(self, news_list):
        """生成邮件内容"""
        body = f"AI新闻日报 - {datetime.now().strftime('%Y年%m月%d日 %H:%M')}\n"
        body += "=" * 60 + "\n\n"

        # 按分类组织新闻
        categories = {}
        for news in news_list:
            cat = news.get('category', '其他')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(news)

        # 输出分类新闻
        for category, items in categories.items():
            body += f"\n【{category}】\n"
            body += "-" * 40 + "\n"

            for i, news in enumerate(items, 1):
                title = news.get('title', '标题缺失')
                summary = news.get('summary', '暂无摘要')[:100]  # 限制摘要长度
                url = news.get('url', '#')
                source = news.get('source', '未知来源')

                body += f"{i}. {title}\n"
                body += f"   来源: {source}\n"
                body += f"   摘要: {summary}\n"
                body += f"   链接: {url}\n\n"

        body += "\n" + "=" * 60 + "\n"
        body += "本邮件由AI新闻聚合系统自动生成\n"

        return body
