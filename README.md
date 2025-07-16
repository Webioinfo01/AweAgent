# AweAgent 使用说明

## install
```
git clone git@github.com:Webioinfo01/AweAgent.git
cd AweAgent
pip install -e .
```

## Usage
```
from agno.utils.pprint import pprint_run_response
from aweagent.agent import PaperAgent

pa = PaperAgent()
rep = pa.run(msg="查询 2025-07-01 到 2025-07-15  AI agent|large language model|foundation model 的论文, 50篇")
pprint_run_response(rep, markdown=True)
```