"""
AI新闻智能总结系统 - 专业版 + 小白版
自动分析和总结最新AI新闻，生成两个版本的理解指南
"""

import json
from datetime import datetime
import sqlite3

# 新闻分类关键词映射
CATEGORY_KEYWORDS = {
    '大模型突破': ['Claude', 'GPT', 'Gemini', 'LLaMA', 'Qwen', '模型', '能力'],
    '推理能力': ['推理', 'reasoning', 'reasoning能力', '逻辑', '数学'],
    '长上下文': ['上下文', 'context', 'token', '长度'],
    '多模态': ['视频', 'audio', '音频', '图像', 'vision', '多模态'],
    '开源': ['开源', '开放', 'open source', 'LLaMA', 'Mistral'],
    '应用产品': ['应用', '产品', 'API', '集成', '部署'],
    '优化效率': ['MoE', 'MOE', '效率', '加速', 'inference', '推理速度'],
    '安全治理': ['安全', '对齐', 'alignment', 'jailbreak'],
    '论文研究': ['论文', 'arxiv', '研究', '算法'],
}

def categorize_news(title, summary=''):
    """根据标题和摘要分类新闻"""
    text = (title + ' ' + summary).lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text:
                return category
    return '其他'

def get_professional_explanation(category, title, summary):
    """生成专业理解版本"""
    explanations = {
        '大模型突破': f"""
【技术突破】{title}
专业解析：涉及参数规模扩大、架构优化或新颖设计，通常指向Scaling Laws的新发现。
关键指标：通常通过基准测试（MMLU、HumanEval等）或特定任务表现提升来衡量。
业界影响：推动AGI进展，改变微调成本-效益曲线，影响产业链投资方向。
技术深度：{summary[:100] if summary else ''}""",

        '推理能力': f"""
【认知升级】{title}
专业解析：模型在逻辑推导、复杂问题分解和多步骤思考中的性能提升。
技术机制：通常涉及Chain-of-Thought、Tree-of-Thoughts等提示工程，或训练阶段的推理强化。
评测方法：通过困难数学题、代码生成、逻辑推理基准测试验证。
应用前景：代码生成、科学计算、策略规划领域价值显著提升。
摘要：{summary[:100] if summary else ''}""",

        '长上下文': f"""
【存储革新】{title}
专业解析：通过架构改进（如ALiBi、Rotary Position Embedding）或硬件优化支持更长的输入序列。
参数：从4K → 8K → 128K → 200K+ tokens的演进。
成本分析：长上下文带来compute成本增加，但enables新应用场景。
应用价值：文档理解、代码库分析、实时多轮对话上下文保留。
详情：{summary[:100] if summary else ''}""",

        '多模态': f"""
【感知融合】{title}
专业解析：模型同时处理文本、图像、视频、音频等多种模态数据的能力。
技术架构：通常采用shared embedding space或cross-modal attention机制。
性能指标：在CLIP-based评估、视频理解基准上的表现。
产业应用：内容创作、自动驾驶感知、医学影像分析。
新进展：{summary[:100] if summary else ''}""",

        '开源': f"""
【开放生态】{title}
专业解析：开源模型降低AI应用成本，加速下游任务定制化微调。
关键数据：模型规模、性能与闭源方案的gap、部署需求（显存）。
生态价值：社区贡献、衍生模型链、本地部署可行性。
行业影响：动摇商业模式，推动端边云协作。
概要：{summary[:100] if summary else ''}""",

        '应用产品': f"""
【落地实践】{title}
专业解析：将AI能力集成到实际产品中，关注用户体验和商业价值。
评估维度：延迟优化、成本控制、准确率权衡、用户采纳度。
竞争格局：API方案 vs 本地部署，功能深度 vs 易用性。
市场机会：垂直领域定制、toB商业化、平台依赖性。
应用说明：{summary[:100] if summary else ''}""",

        '优化效率': f"""
【系统优化】{title}
专业解析：通过Mixture of Experts、量化、蒸馏等技术降低计算成本和延迟。
关键指标：FLOP削减、显存占用、推理吞吐量（tokens/sec）。
工程影响：扩大模型部署范围，支持实时应用。
权衡考量：性能-速度-成本三角的优化边界。
技术细节：{summary[:100] if summary else ''}""",

        '安全治理': f"""
【可靠性保障】{title}
专业解析：从对齐、防护、评估等角度提升模型的安全性和可控性。
技术方案：RLHF、宪法AI、红队测试、自动化防护机制。
政策背景：AI治理框架演进，合规性要求提升。
产品体现：内容审核、个人隐私保护、使用场景限制。
进展：{summary[:100] if summary else ''}""",

        '论文研究': f"""
【科学发现】{title}
专业解析：基础研究成果，可能影响未来模型设计和训练范式。
研究维度：算法创新、理论分析、新基准提出。
引用价值：对业界的指导意义，是否可复现和扩展。
转化周期：从论文到产品通常需要6-18个月。
摘要：{summary[:100] if summary else ''}"""
    }

    return explanations.get(category, f"【{category}】\n{title}\n{summary[:150]}")

def get_simple_explanation(category, title, summary):
    """生成小白理解版本"""
    explanations = {
        '大模型突破': f"""
🚀 {title}
简单说：AI模型又变强了！可能是参数更多、学到的东西更全、回答更准确。
你能感受到：ChatGPT越来越聪明，能回答更难的问题。
生活影响：AI工具越来越好用，搜索、文案、编程都能帮你更好。
""",

        '推理能力': f"""
🧠 {title}
简单说：AI在思考和推理上变强了，能像人一样慢慢分析问题，而不是直接给答案。
你能感受到：问复杂数学题、写复杂代码时，AI能更准确地一步步解决。
生活影响：AI可以帮你分析复杂问题、做逻辑推导，像个智能顾问。
""",

        '长上下文': f"""
📚 {title}
简单说：AI能"记住"更多东西了。从前只能记住几页纸，现在能记住整本书。
你能感受到：把整个文档/代码库丢给AI，它能全部理解，而不是只看前面部分。
生活影响：工作中处理长文档、多轮对话时不用再分段，AI能看全局。
""",

        '多模态': f"""
👁️ {title}
简单说：AI不仅能读字，还能看图、听音频、看视频。就像人类一样全能感知。
你能感受到：上传个视频，AI能理解视频内容，而不只是看图片。
生活影响：AI助手变得更全能，能分析各种内容，如照片、视频、语音。
""",

        '开源': f"""
🎁 {title}
简单说：之前AI只有大公司才能用，现在可以下载下来自己用，还能改进。
你能感受到：不用依赖OpenAI，可以在自己电脑上跑AI模型。
生活影响：成本更低，隐私更好，可以定制自己的AI，创业门槛降低。
""",

        '应用产品': f"""
💡 {title}
简单说：又有新的AI应用上市了，让AI能在生活中真正帮到你。
你能感受到：新App、新功能让工作和生活更便捷，AI不再只是概念。
生活影响：工作效率提升，创意工作变得更容易，重复劳动可以自动化。
""",

        '优化效率': f"""
⚡ {title}
简单说：AI跑得更快了，用的电少了，成本也降低了。
你能感受到：AI回复更快，手机/电脑上就能跑，不用非得连云服务。
生活影响：移动AI普及，响应速度更快，成本更低，隐私更好。
""",

        '安全治理': f"""
🛡️ {title}
简单说：AI被教育得更好了，更听话，不会乱说话或被骗。
你能感受到：AI的回答更安全，隐私信息不被泄露，用着更放心。
生活影响：AI产品更值得信任，可以放心在工作中、日常中使用。
""",

        '论文研究': f"""
📖 {title}
简单说：AI科学家发现了新的方法，可能改变AI的发展方向。
你能感受到：可能不是现在，但几个月后可能有新的更强AI基于这个研究。
生活影响：长期看，这些研究推动AI进步，让未来AI更强更智能。
"""
    }

    return explanations.get(category, f"📰 {title}\n{summary[:150]}")

def generate_summary_report():
    """生成完整的总结报告"""

    # 读取数据库中的新闻
    db_path = r'd:\user\01409715\desktop\待办需求\AI输出\ai_news_system\data\news_cache.db'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 获取最近的新闻
    cursor.execute('''
        SELECT * FROM news
        WHERE push_time > datetime('now', '-1 days')
        ORDER BY push_time DESC
        LIMIT 35
    ''')

    news_records = cursor.fetchall()
    conn.close()

    # 分类汇总
    categorized = {}
    for record in news_records:
        title = record['title']
        source = record['source']
        url = record['url']
        category = record['category']

        # 根据标题进一步细化分类
        detailed_category = categorize_news(title)

        if detailed_category not in categorized:
            categorized[detailed_category] = []

        categorized[detailed_category].append({
            'title': title,
            'source': source,
            'url': url,
            'category': category
        })

    # 生成HTML报告
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI新闻智能总结 - {datetime.now().strftime('%Y年%m月%d日')}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            line-height: 1.6;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .header h1 {{
            font-size: 32px;
            color: #667eea;
            margin-bottom: 10px;
        }}
        .header p {{
            font-size: 14px;
            color: #666;
        }}
        .content {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }}
        @media (max-width: 768px) {{
            .content {{ grid-template-columns: 1fr; }}
        }}
        .panel {{
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .panel-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            font-size: 20px;
            font-weight: bold;
            text-align: center;
        }}
        .panel-content {{
            padding: 20px;
        }}
        .news-item {{
            margin-bottom: 25px;
            padding-bottom: 20px;
            border-bottom: 1px solid #eee;
        }}
        .news-item:last-child {{
            border-bottom: none;
        }}
        .news-title {{
            font-size: 16px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}
        .news-source {{
            font-size: 12px;
            color: #999;
            margin-bottom: 8px;
        }}
        .news-text {{
            font-size: 14px;
            line-height: 1.7;
            color: #666;
            white-space: pre-wrap;
            word-break: break-word;
        }}
        .category-label {{
            display: inline-block;
            background: #f0f0f0;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            color: #667eea;
            margin-top: 10px;
        }}
        .footer {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            color: #999;
            font-size: 12px;
        }}
        .stats {{
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 5px;
            color: white;
            margin-bottom: 20px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI新闻智能总结</h1>
            <p>{datetime.now().strftime('%Y年%m月%d日')} • 一份看懂最新AI进展的指南</p>
        </div>

        <div class="stats">
            <strong>📊 今日统计：</strong>
            共收录 {len(news_records)} 条新闻 |
            {len(categorized)} 个主题方向 |
            更新时间：{datetime.now().strftime('%H:%M')}
        </div>

        <div class="content">
            <div class="panel">
                <div class="panel-header">👨‍💼 专业理解版</div>
                <div class="panel-content" id="professional">
"""

    # 添加专业版内容
    for category in sorted(categorized.keys()):
        items = categorized[category]
        if items:
            news = items[0]
            html_content += f"""
                    <div class="news-item">
                        <div class="news-title">{news['title']}</div>
                        <div class="news-source">来源：{news['source']}</div>
"""
            html_content += f"""
                        <div class="news-text">{get_professional_explanation(category, news['title'], '')}</div>
                        <span class="category-label">#{category}</span>
                    </div>
"""

    html_content += """
                </div>
            </div>

            <div class="panel">
                <div class="panel-header">👶 小白理解版</div>
                <div class="panel-content" id="simple">
"""

    # 添加小白版内容
    for category in sorted(categorized.keys()):
        items = categorized[category]
        if items:
            news = items[0]
            html_content += f"""
                    <div class="news-item">
                        <div class="news-title">{news['title']}</div>
                        <div class="news-source">来源：{news['source']}</div>
"""
            html_content += f"""
                        <div class="news-text">{get_simple_explanation(category, news['title'], '')}</div>
                        <span class="category-label">#{category}</span>
                    </div>
"""

    html_content += """
                </div>
            </div>
        </div>

        <div class="footer">
            <p>💡 提示：左侧为深度技术分析，右侧为通俗易懂解读。建议快速浏览小白版了解概况，再阅读专业版深化理解。</p>
            <p style="margin-top: 10px;">🔗 所有新闻均来自权威AI信息源，更新于每日早8:00</p>
        </div>
    </div>
</body>
</html>
"""

    return html_content, categorized

# 主函数
if __name__ == '__main__':
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("正在生成AI新闻智能总结...")

    try:
        html, categorized = generate_summary_report()

        # 保存HTML文件
        output_path = r'd:\user\01409715\desktop\待办需求\AI输出\ai_news_system\daily_summary.html'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print("总结报告已生成！")
        print(f"位置: {output_path}")
        print(f"分类数: {len(categorized)}")
        print("\n分类如下:")
        for category, items in sorted(categorized.items()):
            print(f"  - {category}: {len(items)}条新闻")

        print("\n双击打开 daily_summary.html 查看完整报告")

    except Exception as e:
        print(f"生成失败: {str(e)}")
