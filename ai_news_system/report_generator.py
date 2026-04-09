"""
AI新闻报告生成模块 - 生成美观的HTML和Markdown报告
支持：分类统计、来源分析、响应式设计
"""
from datetime import datetime
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """报告生成器 - 转换新闻为HTML/Markdown格式"""

    def __init__(self):
        self.news_by_category = defaultdict(list)
        self.stats = {}

    def organize_news_by_category(self, classified_news):
        """按分类组织新闻"""
        self.news_by_category = defaultdict(list)

        for news in classified_news:
            category = news.get('category', '其他')
            self.news_by_category[category].append(news)

        return self.news_by_category

    def calculate_statistics(self, news_list):
        """计算统计信息"""
        sources = defaultdict(int)
        categories = defaultdict(int)

        for news in news_list:
            sources[news.get('source', '未知')] += 1
            categories[news.get('category', '其他')] += 1

        self.stats = {
            'total_news': len(news_list),
            'total_categories': len(categories),
            'total_sources': len(sources),
            'sources': dict(sorted(sources.items(), key=lambda x: x[1], reverse=True)),
            'categories': dict(sorted(categories.items(), key=lambda x: x[1], reverse=True))
        }

        return self.stats

    def generate_html_report(self, classified_news):
        """生成美观的HTML报告"""
        self.organize_news_by_category(classified_news)
        self.calculate_statistics(classified_news)

        html = self._generate_html_template(classified_news)
        return html

    def _generate_html_template(self, news_list):
        """生成HTML邮件模板"""
        stats = self.stats
        categories_data = []

        # 按分类组织显示
        for category in sorted(self.news_by_category.keys()):
            news_items = self.news_by_category[category]
            categories_data.append({
                'name': category,
                'count': len(news_items),
                'news': news_items
            })

        # 生成来源分布HTML
        sources_html = ""
        for source, count in list(stats['sources'].items())[:8]:  # 只显示前8个源
            width = (count / max(stats['sources'].values(), 1)) * 100
            sources_html += f'''
            <div class="source-item">
                <span class="source-name">{source}</span>
                <div class="source-bar">
                    <div class="source-fill" style="width: {width}%"></div>
                </div>
                <span class="source-count">{count}</span>
            </div>
            '''

        # 生成分类卡片HTML
        categories_html = ""
        colors = {
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

        for cat_data in categories_data:
            color = colors.get(cat_data['name'], '#95A5A6')
            categories_html += f'''
            <div class="category-card" style="border-left: 4px solid {color};">
                <div class="category-header">
                    <span class="category-name">{cat_data['name']}</span>
                    <span class="category-count">{cat_data['count']}条</span>
                </div>
                <div class="news-items">
            '''

            # 添加该分类下的新闻
            for i, news in enumerate(cat_data['news'][:5], 1):  # 每个分类最多显示5条
                title = news.get('title', '标题缺失')[:60]
                source = news.get('source', '未知来源')
                url = news.get('url', '#')
                summary = news.get('summary', '暂无摘要')[:80]

                # 专业版和简洁版解读
                pro_explain = news.get('professional_explanation', '')[:100]
                simple_explain = news.get('simple_explanation', '')[:80]

                categories_html += f'''
                <div class="news-item">
                    <div class="news-title">
                        <span class="news-number">{i}</span>
                        <a href="{url}" target="_blank" class="news-link">{title}</a>
                    </div>
                    <div class="news-source">来源: {source}</div>
                    <div class="news-summary">{summary}</div>
                    <div class="news-explanations">
                        <div class="explanation pro"><strong>专业版:</strong> {pro_explain}</div>
                        <div class="explanation simple"><strong>简洁版:</strong> {simple_explain}</div>
                    </div>
                </div>
                '''

            categories_html += '''
                </div>
            </div>
            '''

        html = f'''
<!DOCTYPE html>
<html>
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
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
        }}
        .header h1 {{ font-size: 32px; margin-bottom: 10px; }}
        .header p {{ font-size: 14px; opacity: 0.9; }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            text-align: center;
        }}
        .stat-value {{
            font-size: 28px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 8px;
        }}
        .stat-label {{
            font-size: 13px;
            color: #666;
        }}

        .section {{
            margin-bottom: 30px;
        }}
        .section-title {{
            font-size: 18px;
            font-weight: bold;
            color: #333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}

        .source-list {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        .source-item {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            gap: 10px;
        }}
        .source-name {{
            min-width: 120px;
            font-weight: 500;
            font-size: 13px;
        }}
        .source-bar {{
            flex: 1;
            height: 6px;
            background: #e0e0e0;
            border-radius: 3px;
            overflow: hidden;
        }}
        .source-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.3s ease;
        }}
        .source-count {{
            min-width: 30px;
            text-align: right;
            font-weight: bold;
            color: #667eea;
            font-size: 13px;
        }}

        .categories {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(450px, 1fr));
            gap: 20px;
        }}
        .category-card {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            overflow: hidden;
        }}
        .category-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            background: #f9f9f9;
        }}
        .category-name {{
            font-weight: bold;
            font-size: 15px;
        }}
        .category-count {{
            background: #667eea;
            color: white;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
        }}

        .news-items {{
            padding: 15px;
        }}
        .news-item {{
            padding: 12px 0;
            border-bottom: 1px solid #f0f0f0;
        }}
        .news-item:last-child {{
            border-bottom: none;
        }}

        .news-title {{
            display: flex;
            gap: 10px;
            margin-bottom: 8px;
        }}
        .news-number {{
            color: #667eea;
            font-weight: bold;
            min-width: 24px;
        }}
        .news-link {{
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
            flex: 1;
            word-break: break-word;
        }}
        .news-link:hover {{
            text-decoration: underline;
        }}

        .news-source {{
            font-size: 12px;
            color: #999;
            margin-bottom: 6px;
        }}
        .news-summary {{
            font-size: 13px;
            color: #555;
            margin-bottom: 8px;
            line-height: 1.5;
        }}

        .news-explanations {{
            font-size: 12px;
            background: #f9f9f9;
            padding: 8px;
            border-radius: 6px;
        }}
        .explanation {{
            margin-bottom: 6px;
        }}
        .explanation:last-child {{
            margin-bottom: 0;
        }}
        .explanation strong {{
            color: #667eea;
        }}
        .explanation.pro {{
            color: #5e72e4;
        }}
        .explanation.simple {{
            color: #764ba2;
        }}

        .footer {{
            text-align: center;
            color: #999;
            font-size: 12px;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
        }}

        @media (max-width: 768px) {{
            .categories {{
                grid-template-columns: 1fr;
            }}
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI新闻日报</h1>
            <p>优质内容聚合 • 智能分类解读</p>
            <p style="margin-top: 15px; font-size: 13px;">{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{stats['total_news']}</div>
                <div class="stat-label">条新闻</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats['total_categories']}</div>
                <div class="stat-label">个分类</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats['total_sources']}</div>
                <div class="stat-label">个来源</div>
            </div>
        </div>

        <div class="section">
            <div class="section-title">📊 来源分布</div>
            <div class="source-list">
                {sources_html}
            </div>
        </div>

        <div class="section">
            <div class="section-title">📰 分类新闻</div>
            <div class="categories">
                {categories_html}
            </div>
        </div>

        <div class="footer">
            <p>本邮件由AI新闻聚合系统自动生成</p>
            <p>如有任何问题，请查看系统日志</p>
        </div>
    </div>
</body>
</html>
        '''

        return html

    def generate_markdown_report(self, classified_news):
        """生成Markdown格式报告"""
        self.organize_news_by_category(classified_news)
        self.calculate_statistics(classified_news)

        stats = self.stats
        markdown = f"""# 🤖 AI新闻日报

**生成时间:** {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}

## 📊 统计信息

- **总计新闻数:** {stats['total_news']}条
- **分类数:** {stats['total_categories']}
- **信息源:** {stats['total_sources']}个

### 来源TOP 10

"""

        for source, count in list(stats['sources'].items())[:10]:
            markdown += f"- {source}: {count}条\n"

        markdown += "\n## 📰 分类新闻详览\n\n"

        # 按分类添加新闻
        for category in sorted(self.news_by_category.keys()):
            news_items = self.news_by_category[category]
            markdown += f"### 【{category}】({len(news_items)}条)\n\n"

            for i, news in enumerate(news_items, 1):
                title = news.get('title', '标题缺失')
                source = news.get('source', '未知来源')
                url = news.get('url', '#')
                summary = news.get('summary', '暂无摘要')
                pro = news.get('professional_explanation', '')
                simple = news.get('simple_explanation', '')

                markdown += f"""#### {i}. {title}

- **来源:** {source}
- **链接:** [{url}]({url})
- **摘要:** {summary}
- **专业版:** {pro}
- **简洁版:** {simple}

"""

        markdown += "\n---\n*本报告由AI新闻聚合系统自动生成*\n"

        return markdown
