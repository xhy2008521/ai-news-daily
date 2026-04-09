"""
生成详细的Markdown版本总结
"""
import sqlite3
from datetime import datetime

def categorize_news(title):
    """快速分类"""
    title_lower = title.lower()

    keywords_map = {
        '大模型突破': ['claude', 'gpt', 'gemini', 'llama', 'model', '模型', '能力'],
        '推理能力': ['reasoning', '推理', 'reasoning能力'],
        '长上下文': ['context', 'token', '上下文', '长度'],
        '多模态': ['video', '视频', 'audio', '音频', 'vision', '多模态'],
        '开源': ['open source', '开源', '开放', 'llama'],
        '应用产品': ['app', 'api', '应用', '产品', '集成'],
        '优化效率': ['moe', 'efficient', '效率', '加速'],
        '安全治理': ['safe', 'alignment', '安全', '对齐'],
        '论文研究': ['paper', 'arxiv', '论文', '研究'],
    }

    for category, keywords in keywords_map.items():
        for kw in keywords:
            if kw in title_lower:
                return category
    return '其他'

# 读取数据库
db_path = r'd:\user\01409715\desktop\待办需求\AI输出\ai_news_system\data\news_cache.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''
    SELECT title, source, category FROM news
    WHERE push_time > datetime('now', '-1 days')
    ORDER BY source, title
''')

records = cursor.fetchall()
conn.close()

# 按分类整理
categorized = {}
for title, source, category in records:
    detailed_cat = categorize_news(title)
    if detailed_cat not in categorized:
        categorized[detailed_cat] = []
    categorized[detailed_cat].append({
        'title': title,
        'source': source,
        'category': category
    })

# 生成Markdown
markdown = f"""# AI新闻日报 - {datetime.now().strftime('%Y年%m月%d日')}

> 🤖 智能总结你关心的AI前沿进展 | 专业版 + 小白版双重解读

---

## 📊 今日数据

| 项目 | 数值 |
|------|------|
| **总新闻数** | {len(records)} 条 |
| **分类数** | {len(categorized)} 个 |
| **更新时间** | {datetime.now().strftime('%H:%M:%S')} |

---

## 🎯 分类导航

"""

# 添加分类导航
for cat in sorted(categorized.keys()):
    count = len(categorized[cat])
    markdown += f"- [{cat}](#{cat}) ({count}条)\n"

markdown += "\n---\n\n"

# 生成详细内容
category_icons = {
    '大模型突破': '🚀',
    '推理能力': '🧠',
    '长上下文': '📚',
    '多模态': '👁️',
    '开源': '🎁',
    '应用产品': '💡',
    '优化效率': '⚡',
    '安全治理': '🛡️',
    '论文研究': '📖',
    '其他': '📰'
}

for category in sorted(categorized.keys()):
    items = categorized[category]
    icon = category_icons.get(category, '📌')

    markdown += f"\n## {icon} {category}\n\n"

    for i, item in enumerate(items, 1):
        markdown += f"### {i}. {item['title']}\n"
        markdown += f"**来源**: {item['source']} | **分类**: {item['category']}\n\n"

        # 根据分类生成简要分析
        title = item['title']

        if '大模型' in category or '突破' in category:
            markdown += """**专业版**: 通过参数扩展、架构优化或训练方法创新，模型在多个基准测试上实现性能突破。通常通过MMLU、HumanEval等权威评测验证新能力。

**小白版**: AI又变聪明了！可能是能记住更多东西、回答更准确、处理更复杂问题。你会发现AI工具用起来更好用。

"""

        elif '推理' in category:
            markdown += """**专业版**: 模型在复杂问题分解、逻辑推导、多步骤思考中的性能提升。通常通过Chain-of-Thought、复杂数学题、代码生成基准验证。

**小白版**: AI在思考上变强了，能像人一样一步步分析问题，而不是直接给答案。问复杂数学题或写复杂代码时更准确。

"""

        elif '长上下文' in category or '上下文' in category:
            markdown += """**专业版**: 通过位置编码改进（RoPE、ALiBi）、KV缓存优化等实现更长的输入序列处理。支持从4K到200K+tokens的演进。

**小白版**: AI能"记住"更多东西了。从前只能看几页纸，现在能看整本书，处理长文档时完全理解上下文。

"""

        elif '多模态' in category:
            markdown += """**专业版**: 模型在处理文本、图像、视频、音频等多种模态数据时的能力提升。通常采用共享embedding space和cross-modal attention。

**小白版**: AI不仅能读字，还能看图、听音频、看视频。上传个视频，AI能理解内容，就像人类一样全能感知。

"""

        elif '开源' in category:
            markdown += """**专业版**: 开源模型降低部署成本，支持本地化微调，加速下游应用定制。推动端边云协作，衍生出丰富的模型生态。

**小白版**: AI不再只有大公司能用，可以下载下来自己用。成本更低，隐私更好，可以定制自己的AI。

"""

        elif '应用' in category or '产品' in category:
            markdown += """**专业版**: AI能力在实际产品中的工程化落地。关注延迟、成本、准确率的权衡，以及用户采纳度。

**小白版**: 新的AI应用上市了，让AI能在生活中真正帮到你。工作效率提升，重复劳动可以自动化。

"""

        elif '效率' in category or '优化' in category:
            markdown += """**专业版**: 通过MoE、量化、蒸馏等技术降低compute成本和延迟。关键指标：FLOP削减、显存占用、吞吐量。

**小白版**: AI跑得更快了，用的电少了。手机/电脑上就能跑，响应速度更快，成本也更低。

"""

        elif '安全' in category or '治理' in category:
            markdown += """**专业版**: 从RLHF、防护、红队测试等角度提升模型的对齐度和可控性。政策治理框架不断演进。

**小白版**: AI被教育得更好了，更听话，不会乱说话。隐私信息不被泄露，用着更放心。

"""

        elif '论文' in category or '研究' in category:
            markdown += """**专业版**: 基础研究成果可能影响未来模型架构和训练范式。需要关注可复现性和扩展潜力。

**小白版**: AI科学家发现了新方法，几个月后可能就有新的更强AI基于这个研究。长期推动AI进步。

"""

        else:
            markdown += """**专业版**: 关注行业动向、政策影响等全局信息。

**小白版**: 了解AI发展的大趋势，理解当前AI领域的主要方向。

"""

        markdown += "---\n"

# 添加尾部
markdown += f"""

## 💡 使用建议

1. **快速浏览**: 按分类扫一遍小白版，5分钟内了解今天AI界发生了什么
2. **深度学习**: 对感兴趣的分类，点击阅读专业版，理解技术细节
3. **追踪动向**: 关注"大模型突破"和"论文研究"分类，掌握核心进展

## 🔔 下次推送

⏰ **明天早上8:00** 将为你推送新一期AI新闻日报

> 本报告由 AI新闻聚合系统 自动生成 | 数据来源: 36氪、量子位、机器之心、arXiv、Hacker News等
"""

# 保存
output_path = r'd:\user\01409715\desktop\待办需求\AI输出\ai_news_system\daily_summary.md'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(markdown)

print(f"Markdown版本已生成: {output_path}")
print(f"包含{len(records)}条新闻")
