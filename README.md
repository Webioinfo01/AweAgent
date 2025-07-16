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
    msg="""查询 2025-07-01 到 2025-07-15  AI agent|large language model|foundation model 的论文,
     fieds: "paperId",  "externalIds", "url", "title", "abstract", "venue", "publicationVenue", "publicationTypes", "publicationDate", "journal", "authors", "citations"
    """
    )
pprint_run_response(rep, markdown=True)

```