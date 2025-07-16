import pandas as pd
from pathlib import Path
from agno.agent import Agent
from agno.models.deepseek import DeepSeek
from agno.workflow import Workflow
from agno.run.response import RunResponse

from textwrap import dedent
from pydantic import BaseModel, Field
from typing import Literal
from .tool import search_papers


class PaperModel(BaseModel):
    doi: str = Field(description="The paper DOI")
    title: str = Field(description="The title of the paper")
    domain: str = Field(description="The research domain of the paper")
    category: str = Field(description="The category of the paper")
    journal: str = Field(description="The journal of the paper")
    authors: str = Field(description="The authors of the paper")
    publicationDate: str = Field(description="The publication date of the paper")
    url: str = Field(description="The url of the paper")
    venue: str = Field(description="The venue of the paper")

    
class PaperListModel(BaseModel):
    paper_list: list[PaperModel] = Field(description="The list of papers")


class PaperAgent(Workflow):

    searcher = Agent(
        name="searcher",
        model=DeepSeek(id="deepseek-chat"),
        description="Paper search",
        tools=[search_papers],
        instructions=dedent("""
            You are a paper search agent. you need to search the paper from the Semantic Scholar.
            return full output from tool calling.
            if the paper is not found, return an empty list.
            
            Tool calling specification:
            - search_papers:
                - publication_date_or_year: [start_date, end_date]
                        <start_date>:<end_date>, where dates are in the format YYYY-MM-DD, YYYY-MM, or YYYY	

        """),
        show_tool_calls=True,
    )

    annotator = Agent(
        name="annotator",
        model=DeepSeek(id="deepseek-chat"),
        description="Paper annotator",
        instructions=dedent("""
            You are a paper annotator. you need to annotate the papers from a list of papers.
            You should annotate the papers based on:
            - The paper domain
            - The paper category, if user provide a category list, you should annotate the papers based on the category list.
            
           Filter the papers that are published in the bad journal. keep papers which published in pre-print server.
        """),
        response_model=PaperListModel,
        use_json_mode=True,
        show_tool_calls=True,
    )

    reporter = Agent(
        name="reporter",
        model=DeepSeek(id="deepseek-chat"),
        description="Paper reporter",
        instructions=dedent("""
            你是一个论文报告生成 Agent。你的任务是根据用户的输入的论文数据，按照 category 对论文进行分组，为每个 category 生成一个独立的 section。每个 section 以二级标题 (## {category}) 开头，并包含一个 markdown 表格，表格字段为：DOI、Title、Domain、Journal、Date。

            输出一个结构清晰、可直接用作 readme.md 的 markdown 文档。自行添加合适的Table of Contents，introduction。确保是一个完整的报告。

            示例输出：

            ## AI Agents
            | DOI | Title | Domain | Journal | publicationDate |
            |-----|-------|--------|---------|------|
            | 10.1234/abc | Example Paper | Biology | Nature | 2023-01-01 |

            ## Foundation Models
            | DOI | Title | Domain | Journal | publicationDate |
            |-----|-------|--------|---------|------|
            | 10.5678/def | Another Paper | Computer Science | arXiv | 2022-12-12 |
        """),
        markdown=True,
        show_tool_calls=True,
    )


    def run(self, msg):
        rep = self.searcher.run(msg)
        annotator_res = self.annotator.run(rep.content)
        paper_list = annotator_res.content.model_dump()['paper_list']
        query_paper_res = self.query_paper(paper_list)
        readme = self.reporter.run(str(query_paper_res))
        with open("readme.md", "w", encoding="utf-8") as f:
            f.write(readme.content)
        return readme

    def query_paper(self, paper_list):
        from .db import get_database_session, Paper

        doi_list = [i['doi'] for i in paper_list]
        session = get_database_session()
        papers = session.query(Paper).filter(Paper.doi.in_(doi_list)).all()
        result = []
        doi_to_paper = {paper.doi: paper for paper in papers}
        for idx, doi in enumerate(doi_list):
            paper = doi_to_paper.get(doi)
            result.append({
                'doi': paper.doi,
                'title': paper.title,
                'authors': paper.authors,
                'publicationDate': paper.publicationDate,
                'url': paper.url,
                'domain': paper_list[idx]['domain'],
                'category': paper_list[idx]['category'],
                'venue': paper.venue,
                'journal': paper.journal
            })
        return result
        
