from agno.workflow import Workflow
from textwrap import dedent
import os

from .agents import create_annotator_agent, create_reporter_agent, create_searcher_agent
from .db import get_database_session, Paper


class PaperAgent(Workflow):
    def __init__(self, model, semanticscholar_api_key: str | None = None, status_callback=None):
        self.status_callback = status_callback
        self.searcher = create_searcher_agent(model, semanticscholar_api_key)
        self.annotator = create_annotator_agent(model)
        self.reporter = create_reporter_agent(model)

    def run(self, msg, db_path=None):
        if self.status_callback: self.status_callback("Searching for papers...")
        rep = self.searcher.run(msg)

        if self.status_callback: self.status_callback("Annotating papers...")
        annotator_res = self.annotator.run(rep.content)
        while isinstance(annotator_res.content, str):
            annotator_res = self.annotator.run(annotator_res.content)
        paper_list = annotator_res.content.model_dump()["paper_list"]
        
        if self.status_callback: self.status_callback("Querying database for details...")
        query_paper_res = self.query_paper(paper_list, db_path)
        
        if self.status_callback: self.status_callback("Generating report...")
        return self.reporter.run(str(query_paper_res))

    def query_paper(self, paper_list, db_path=None):
        doi_list = [i["doi"] for i in paper_list]
        session = get_database_session(db_path)
        
        filter_db_full_path = os.path.join(db_path, "SemanticScholar_papers_filter.db") if db_path else "SemanticScholar_papers_filter.db"
        database_filter_url = f"sqlite:///{filter_db_full_path}"
        
        session_filter = get_database_session(os.path.dirname(filter_db_full_path) if db_path else None)
        papers = session.query(Paper).filter(Paper.doi.in_(doi_list)).all()
        result = {}
        doi_to_paper = {paper.doi: paper for paper in papers}
        for idx, doi in enumerate(doi_list):
            paper = doi_to_paper.get(doi)
            result.setdefault(paper_list[idx]["category"], []).append(
                {
                    "doi": paper.doi,
                    "title": paper.title,
                    "authors": paper.authors,
                    "publicationDate": paper.publicationDate,
                    "url": paper.url,
                    "domain": paper_list[idx]["domain"],
                    "category": paper_list[idx]["category"],
                    "venue": paper.venue,
                    "journal": paper.journal,
                }
            )
            existing = session_filter.query(Paper).filter_by(doi=doi).first()
            if not existing:
                session_filter.add(
                    Paper(
                        doi=doi,
                        title=paper.title,
                        authors=paper.authors,
                        publicationDate=paper.publicationDate,
                        url=paper.url,
                        domain=paper_list[idx]["domain"],
                        category=paper_list[idx]["category"],
                        venue=paper.venue,
                        journal=paper.journal,
                    )
                )
        return result 