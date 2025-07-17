# AweAgent 使用说明

## install
```
git clone git@github.com:Webioinfo01/AweAgent.git
cd AweAgent
pip install -e .
```

## Usage

api key set
```bash
export DEEPSEEK_API_KEY="sk-**"
export SEMANTICSCHOLAR_API_KEY="sk-**"
```
demo
```python
from agno.utils.pprint import pprint_run_response
from aweagent.agent import PaperAgent

pa = PaperAgent()
rep = pa.run(
    msg="""
    查询论文：
     query: AI agent|large language model|foundation model
     publication_date: 2025-07-01 到 2025-07-15
     limit: 100
     fields: "paperId",  "externalIds", "url", "title", "abstract", "venue", "publicationVenue", "publicationTypes", "publicationDate", "journal", "authors", "citations"
     fields_of_study: "Medicine",  "Biology"
    
    pre-defined category: ["AI agent", "AI Tools", "Foundation Models", "Databases", "Benchmarks", "Reviews"]
    )
    """
)
pprint_run_response(rep, markdown=True)
```