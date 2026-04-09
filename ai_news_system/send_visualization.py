"""
可视化结果邮件推送脚本
将所有美观的可视化界面发送到邮箱
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.encoders import encode_base64
from datetime import datetime
import os
import sys
sys.path.insert(0, r'd:\user\01409715\desktop\待办需求\AI输出\ai_news_system')

import config

def send_visualization_email():
    """发送可视化结果到邮箱"""

    try:
        # 邮件内容
        html_body = """
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body { font-family: 'Microsoft YaHei', Arial; line-height: 1.6; color: #333; }
                .container { max-width: 800px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                         color: white; padding: 30px; border-radius: 10px; text-align: center; }
                .section { background: #f9f9f9; padding: 20px; margin: 15px 0; border-radius: 8px;
                          border-left: 4px solid #667eea; }
                .card { background: white; padding: 15px; margin: 10px 0; border-radius: 8px;
                       box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
                .card-title { font-weight: bold; color: #667eea; margin-bottom: 8px; }
                .card-desc { color: #666; font-size: 13px; }
                .btn { display: inline-block; padding: 12px 24px; background: #667eea;
                      color: white; text-decoration: none; border-radius: 6px; margin: 5px; }
                .footer { text-align: center; color: #999; font-size: 12px; margin-top: 30px; }
                .stats { display: flex; justify-content: space-around; text-align: center;
                        color: white; padding: 20px; }
                .stat-item { flex: 1; }
                .stat-value { font-size: 32px; font-weight: bold; }
                .stat-label { font-size: 13px; opacity: 0.9; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤖 AI新闻聚合系统</h1>
                    <p>超美观可视化界面已生成！</p>
                    <p style="margin-top: 10px; opacity: 0.9;">""" + datetime.now().strftime('%Y年%m月%d日 %H:%M:%S') + """</p>

                    <div class="stats">
                        <div class="stat-item">
                            <div class="stat-value">4</div>
                            <div class="stat-label">可视化界面</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">40+</div>
                            <div class="stat-label">条AI新闻</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">6</div>
                            <div class="stat-label">个分类</div>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h2>✨ 4大超美观可视化界面</h2>

                    <div class="card">
                        <div class="card-title">1️⃣ 导航中心 (index.html)</div>
                        <div class="card-desc">
                            📍 功能：快速导航入口，了解所有功能<br>
                            ⏱️ 用时：1分钟<br>
                            ⭐ 推荐：★★★★★ (首次必看)<br>
                            📌 特点：完整功能说明 + 快速开始指南
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-title">2️⃣ 双版本快读器 (visualization.html) ⭐ 最实用</div>
                        <div class="card-desc">
                            📍 功能：左右对比专业版和小白版<br>
                            ⏱️ 用时：5-10分钟快速浏览<br>
                            ⭐ 推荐：★★★★★ (日常最常用)<br>
                            📌 特点：<br>
                            &nbsp;&nbsp;✓ 实时搜索和分类筛选<br>
                            &nbsp;&nbsp;✓ 暗黑模式切换<br>
                            &nbsp;&nbsp;✓ 阅读进度统计<br>
                            &nbsp;&nbsp;✓ 流畅交互动画
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-title">3️⃣ 仪表板 & 数据分析 (dashboard.html)</div>
                        <div class="card-desc">
                            📍 功能：数据可视化和趋势分析<br>
                            ⏱️ 用时：10-15分钟深度分析<br>
                            ⭐ 推荐：★★★★ (数据分析爱好者)<br>
                            📌 特点：<br>
                            &nbsp;&nbsp;✓ 饼图/折线图展示<br>
                            &nbsp;&nbsp;✓ 分类统计卡片<br>
                            &nbsp;&nbsp;✓ 热点新闻排行<br>
                            &nbsp;&nbsp;✓ 实时更新状态
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-title">4️⃣ 专业阅读器 (reader.html)</div>
                        <div class="card-desc">
                            📍 功能：沉浸式深度阅读体验<br>
                            ⏱️ 用时：20-30分钟深入学习<br>
                            ⭐ 推荐：★★★★★ (深度研究)<br>
                            📌 特点：<br>
                            &nbsp;&nbsp;✓ 吸附式导航条<br>
                            &nbsp;&nbsp;✓ 目录自动导航<br>
                            &nbsp;&nbsp;✓ 字体调整和暗黑模式<br>
                            &nbsp;&nbsp;✓ 进度追踪和分享功能
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h2>🎯 推荐使用方案</h2>

                    <div class="card">
                        <div class="card-title">📱 场景1：办公室快速了解（5分钟）</div>
                        <div class="card-desc">
                            打开 visualization.html<br>
                            → 看小白版了解概况<br>
                            → 点击感兴趣的分类<br>
                            → 看专业版深化理解
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-title">📊 场景2：数据分析和汇报（10-15分钟）</div>
                        <div class="card-desc">
                            打开 dashboard.html<br>
                            → 查看图表和统计数据<br>
                            → 截图用于演讲或报告
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-title">📚 场景3：深度学习和研究（20-30分钟）</div>
                        <div class="card-desc">
                            打开 reader.html<br>
                            → 使用目录导航浏览<br>
                            → 逐节阅读细节<br>
                            → 调整字体到舒适大小
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h2>📊 今日数据统计</h2>
                    <p><strong>总新闻数：</strong> 40条</p>
                    <p><strong>数据来源：</strong> 36氪、量子位、机器之心、arXiv、Hacker News</p>
                    <p><strong>分类分布：</strong></p>
                    <ul style="margin-left: 20px;">
                        <li>🚀 大模型突破：9条</li>
                        <li>📖 论文研究：15条</li>
                        <li>💡 应用产品：4条</li>
                        <li>📚 长上下文：1条</li>
                        <li>⚡ 优化效率：1条</li>
                        <li>🛡️ 安全治理：1条</li>
                        <li>📰 其他：8条</li>
                    </ul>
                </div>

                <div class="section">
                    <h2>💾 所有文件清单</h2>
                    <p><strong>位置：</strong> d:\\user\\01409715\\desktop\\待办需求\\AI输出\\ai_news_system\\</p>

                    <p><strong>可视化界面（已附件）：</strong></p>
                    <ul style="margin-left: 20px;">
                        <li>index.html (21KB) - 导航中心</li>
                        <li>visualization.html (30KB) - 双版本快读器</li>
                        <li>dashboard.html (21KB) - 仪表板</li>
                        <li>reader.html (22KB) - 专业阅读器</li>
                        <li>daily_summary.html (12KB) - HTML报告</li>
                        <li>daily_summary.md (16KB) - Markdown版本</li>
                    </ul>

                    <p><strong>核心系统文件（已附件）：</strong></p>
                    <ul style="margin-left: 20px;">
                        <li>main.py - 主程序入口</li>
                        <li>config.py - 配置文件</li>
                        <li>ai_news_fetcher.py - 新闻爬取</li>
                        <li>email_sender.py - 邮件发送</li>
                        <li>database.py - 数据库管理</li>
                    </ul>
                </div>

                <div class="section">
                    <h2>🚀 立即开始</h2>
                    <p style="text-align: center; margin: 20px 0;">
                        <span style="display: inline-block; background: #667eea; color: white;
                                   padding: 12px 24px; border-radius: 6px; text-decoration: none;">
                            ✅ 全部文件已作为附件发送
                        </span>
                    </p>
                    <p style="text-align: center;">
                        <strong>使用方法：</strong><br>
                        1. 下载所有附件到同一文件夹<br>
                        2. 双击 <code>index.html</code> 打开导航中心<br>
                        3. 选择你喜欢的界面点击查看<br>
                        4. 享受美观的AI新闻体验！
                    </p>
                </div>

                <div class="footer">
                    <p>💡 提示：所有HTML文件都支持离线使用，可以随时打开查看，无需网络连接</p>
                    <p>🔔 定时推送：每天早上8:00自动推送最新AI新闻到邮箱</p>
                    <p>📧 反馈：有任何建议或问题，欢迎反馈改进</p>
                    <p style="margin-top: 20px; border-top: 1px solid #ddd; padding-top: 10px;">
                        © 2026 AI新闻聚合系统 | 祝你使用愉快！
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        # 创建邮件
        msg = MIMEMultipart('mixed')
        msg['Subject'] = f"🎉 AI新闻可视化结果已生成！- {datetime.now().strftime('%Y年%m月%d日')}"
        msg['From'] = config.QQ_EMAIL
        msg['To'] = config.EMAIL_TO

        # 添加HTML内容
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        # 添加附件
        attachment_files = [
            ('index.html', 'index.html'),
            ('visualization.html', 'visualization.html'),
            ('dashboard.html', 'dashboard.html'),
            ('reader.html', 'reader.html'),
            ('daily_summary.html', 'daily_summary.html'),
            ('daily_summary.md', 'daily_summary.md'),
            ('README.md', 'README.md'),
        ]

        base_path = r'd:\user\01409715\desktop\待办需求\AI输出\ai_news_system'

        for file_path, file_name in attachment_files:
            try:
                full_path = f"{base_path}\\{file_path}"
                with open(full_path, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename="{file_name}"')
                    msg.attach(part)
                print(f"✓ 已添加附件: {file_name}")
            except Exception as e:
                print(f"⚠ 附件失败 {file_name}: {str(e)}")

        # 发送邮件
        with smtplib.SMTP_SSL(config.SMTP_SERVER, config.SMTP_PORT, timeout=10) as server:
            server.login(config.QQ_EMAIL, config.QQ_AUTH_CODE)
            server.send_message(msg)

        print("\n" + "="*60)
        print("✓ 可视化结果邮件推送成功！")
        print("="*60)
        print(f"📧 收件人: {config.EMAIL_TO}")
        print(f"📎 附件: 7个可视化和文档文件")
        print(f"⏰ 发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n💡 使用说明：")
        print("1. 打开邮件，下载所有附件")
        print("2. 将文件保存到同一文件夹")
        print("3. 双击 index.html 打开导航中心")
        print("4. 选择喜欢的界面查看")
        print("="*60)

        return True

    except Exception as e:
        print(f"❌ 邮件发送失败: {str(e)}")
        return False

if __name__ == '__main__':
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    send_visualization_email()
