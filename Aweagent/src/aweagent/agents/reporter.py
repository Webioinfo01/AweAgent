from agno.agent import Agent
from textwrap import dedent

def create_reporter_agent(model):
    reporter = Agent(
        name="reporter",
        model=model,
        description="Paper reporter",
        instructions=dedent("""
            你是一个论文报告生成 Agent。你的任务是根据用户的输入的论文数据，按照 category 对论文进行分组，为每个 category 生成一个独立的 section。每个 section 以二级标题 (## {category}) 开头，并包含一个 markdown 表格，表格字段为：DOI、Title、Domain、Journal、Date。

            输出一个结构清晰、可直接用作 readme.md 的 markdown 文档。自行添加合适的Table of Contents，introduction。确保是一个完整的报告。

            示例输出：

            ## AI Agents
            | DOI | Title | Domain | Journal | publicationDate | Authors | Affiliations |
            |-----|-------|--------|---------|------|------|------|
            | 10.1234/abc | Example Paper | Biology | Nature | 2023-01-01 | John Doe | University of California, Los Angeles |

            ## Foundation Models
            | DOI | Title | Domain | Journal | publicationDate | Authors | Affiliations |
            |-----|-------|--------|---------|------|------|------|
            | 10.5678/def | Another Paper | Computer Science | arXiv | 2022-12-12 | Jane Smith | University of Oxford |
                            
            WARNING:
            You should return directly markdown content. Not return ```markdown content```
        """),
        markdown=True,
        show_tool_calls=True,
    )
    return reporter 