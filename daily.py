from aweagent.agent import PaperAgent
from datetime import datetime, timedelta
import os


os.environ["DATABASE_URL"] = "sqlite:///daily_report/SemanticScholar_papers.db"
os.environ["DATABASE_FILTER_URL"] = (
    "sqlite:///daily_report/SemanticScholar_papers_filter.db"
)


today = datetime.now().strftime("%Y-%m-%d")
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
pa = PaperAgent()
rep = pa.run(
    msg=f"""
    查询论文：
     query: AI agent|large language model|foundation model
     publication_date: {yesterday} 到 {today}
     limit: 100
     fields: "paperId",  "externalIds", "url", "title", "abstract", "venue", "publicationVenue", "publicationTypes", "publicationDate", "journal", "authors", "citations"
     fields_of_study: "Medicine",  "Biology"
    
    pre-defined category: ["AI agent", "AI Tools", "Foundation Models", "Databases", "Benchmarks", "Reviews"]
    """
)

with open(f"daily_report/{today}.md", "w", encoding="utf-8") as f:
    f.write(rep.content)
