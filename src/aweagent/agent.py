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
import os

class PaperModel(BaseModel):
    doi: str = Field(description="The paper DOI")
    domain: str = Field(description="The research domain of the paper")
    category: str = Field(description="The category of the paper")

    
class PaperListModel(BaseModel):
    paper_list: list[PaperModel] = Field(description="The list of papers")
    category_list: list[str] = Field(description="The list of categories")


model = DeepSeek(id="deepseek-chat")

class PaperAgent(Workflow):

    searcher = Agent(
        name="searcher",
        model=model,
        description="Paper search",
        tools=[search_papers],
        instructions=dedent("""
            You are a paper search agent. you need to search the paper from the Semantic Scholar.
            return full output from tool calling.
            if the paper is not found, return an empty list.
            
            Tool calling specification:
            - search_papers:
                - query (str): Plain-text search query string. don't be confused with the predefined category list.
                - publication_date_or_year: [start_date, end_date]
                        <start_date>:<end_date>, where dates are in the format YYYY-MM-DD, YYYY-MM, or YYYY	
            
            you should return result following template:
            <output>
                <search_papers_response>
                    [query_result]
                </search_papers_response>
                <predefined_category_list>
                    [category_list]
                </predefined_category_list>
            </output>
            Note: if user do not provide a category list, leave the category_list empty.

        """),
        show_tool_calls=True,
    )

    annotator = Agent(
        name="annotator",
        model=model,
        description="Paper annotator",
        instructions=dedent("""
            You are a paper annotator. you need to annotate the papers from user provided papers and category list using paper title.
            You should annotate the papers based on:
            - The paper domain, infer from paper title
            - The paper category if user provide a category list, you should select the category from the provided category list.
            
            Note: You will return the paper list and the category list.
            Note: category list is a list of categories that the user provided, if user not provide a category list, you should annotate the category based on the paper title.
            Note: You should double check the paper category are belong to the provided category list.
        """),
        response_model=PaperListModel,
        use_json_mode=True,
        show_tool_calls=True,
    )

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
        """),
        markdown=True,
        show_tool_calls=True,
    )

    def run(self, msg):
        rep = self.searcher.run(msg)
        annotator_res = self.annotator.run(rep.content)
        while isinstance(annotator_res.content, str):
            annotator_res = self.annotator.run(annotator_res.content)
        paper_list = annotator_res.content.model_dump()['paper_list']
        query_paper_res = self.query_paper(paper_list)
        return self.reporter.run(str(query_paper_res))

    def query_paper(self, paper_list):
        from .db import get_database_session, Paper

        doi_list = [i['doi'] for i in paper_list]
        session = get_database_session()
        database_filter_url = os.getenv("DATABASE_FILTER_URL", "sqlite:///SemanticScholar_papers_filter.db")
        session_filter = get_database_session(database_filter_url)
        papers = session.query(Paper).filter(Paper.doi.in_(doi_list)).all()
        result = {}
        doi_to_paper = {paper.doi: paper for paper in papers}
        for idx, doi in enumerate(doi_list):
            paper = doi_to_paper.get(doi)
            result.setdefault(paper_list[idx]['category'], []).append({
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
            existing = session_filter.query(Paper).filter_by(doi=doi).first()
            if not existing:
                session_filter.add(Paper(
                    doi=doi,
                    title=paper.title,
                    authors=paper.authors,
                    publicationDate=paper.publicationDate,
                    url=paper.url,
                    domain=paper_list[idx]['domain'],
                    category=paper_list[idx]['category'],
                    venue=paper.venue,
                    journal=paper.journal
                ))
        return result
