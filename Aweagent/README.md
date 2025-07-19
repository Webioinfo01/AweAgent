# AweAgent: Automated Scientific Paper Discovery and Summarization

## Overview

AweAgent is an AI-powered agent built using the [Agno framework](https://docs.agno.com/) designed to automate the process of discovering, filtering, and summarizing scientific papers. Its primary goal is to help users keep their knowledge bases, such as a GitHub project like `Awesome-AI-Meets-Biology`, updated with the latest and most relevant research.

## Features

-   **Automated Paper Discovery:** Integrates with the Semantic Scholar API to search for scientific papers based on specified queries and filters.
-   **Intelligent Annotation:** Categorizes papers by research domain and assigns relevant categories, either from predefined lists or inferred from paper titles.
-   **Structured Report Generation:** Creates well-organized Markdown reports, grouping papers by category into tables with key information (DOI, Title, Domain, Journal, Publication Date).
-   **Local Data Persistence:** Caches retrieved paper data in local SQLite databases (`SemanticScholar_papers.db` and `SemanticScholar_papers_filter.db`) to reduce redundant API calls and store results efficiently.
-   **Modular Architecture:** Designed with a clear separation of concerns, utilizing distinct Agno agents (`Searcher`, `Annotator`, `Reporter`) for enhanced maintainability and scalability.

## Project Structure

```
Aweagent/
├── src/
│   └── aweagent/
│       ├── agents/
│       │   ├── annotator.py
│       │   ├── reporter.py
│       │   └── searcher.py
│       │   └── __init__.py
│       ├── __init__.py
│       ├── db.py
│       ├── tool.py
│       └── workflow.py
├── .env.example (or .env file)
├── main.py
└── pyproject.toml
```

## Installation

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone <your-repository-url>
    cd Aweagent
    ```

2.  **Navigate to the project directory:**
    ```bash
    cd 250717-AweAgent/Aweagent
    ```

3.  **Install dependencies:**
    ```bash
    pip install .
    ```

## Configuration

To configure the AweAgent, you will primarily use environment variables. Create a `.env` file in the `250717-AweAgent/Aweagent` directory.

### Model Selection and API Keys

Set the `MODEL_PROVIDER` environment variable to choose your desired LLM. If `MODEL_PROVIDER` is not set, `openai` will be used by default. Based on your selection, you'll need to provide the corresponding API key.

-   **OpenAIChat (default):**
    ```dotenv
    MODEL_PROVIDER="openai"
    OPENAI_API_KEY="your_openai_api_key_here"
    ```

-   **DeepSeek:**
    ```dotenv
    MODEL_PROVIDER="deepseek"
    DEEPSEEK_API_KEY="your_deepseek_api_key_here"
    ```

-   **Gemini:**
    ```dotenv
    MODEL_PROVIDER="gemini"
    GOOGLE_API_KEY="your_google_api_key_here"
    ```

-   **MistralChat:**
    ```dotenv
    MODEL_PROVIDER="mistral"
    MISTRAL_API_KEY="your_mistral_api_key_here"
    ```

-   **OpenAILike (for self-hosted or compatible APIs):**
    ```dotenv
    MODEL_PROVIDER="openaillm"
    OPENAI_API_KEY="your_openai_api_key_here"
    OPENAI_BASE_URL="your_openai_like_base_url_here"
    ```

### Semantic Scholar API Key

Regardless of the LLM model, you also need to configure your Semantic Scholar API key:

```dotenv
SEMANTICSCHOLAR_API_KEY="your_semantic_scholar_api_key_here"
```

### Database Configuration

(Optional) You can customize the database paths:

```dotenv
DATABASE_URL="sqlite:///SemanticScholar_papers.db"
DATABASE_FILTER_URL="sqlite:///SemanticScholar_papers_filter.db"
```

### Direct Input to Agent (Alternative)

Alternatively, you can pass the `model` object and `semanticscholar_api_key` directly to the `PaperAgent` constructor in your code:

```python
from src.aweagent import PaperAgent
from agno.models import DeepSeek # or OpenAIChat, Gemini, MistralChat, OpenAILike
import os

# Example with DeepSeek model
model = DeepSeek(api_key=os.getenv("DEEPSEEK_API_KEY"))
agent = PaperAgent(model=model, semanticscholar_api_key=os.getenv("SEMANTICSCHOLAR_API_KEY"))

# Example with OpenAILike model (requires base_url)
# model = OpenAILike(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL"))
# agent = PaperAgent(model=model, semanticscholar_api_key=os.getenv("SEMANTICSCHOLAR_API_KEY"))
```

## Usage

To run the AweAgent, execute the `main.py` script. It will guide you through an interactive setup process:

```bash
python main.py
```

### Interactive Setup

1.  **Select AI Model:** You will be prompted to choose an AI model provider from a list (OpenAI, DeepSeek, Gemini, etc.).
2.  **Enter API Keys:** You will be prompted to enter the API key for your chosen model and for the Semantic Scholar service. If an input is left empty, you will be re-prompted until a valid key is provided.
3.  **Set Database Path:** You can specify a directory to store the Semantic Scholar database files (defaults to `./SemanticScholar_db/`).
4.  **Choose Output Method:** You can choose to have the final report printed to the screen or saved to a file (e.g., `research_report.md`).
5.  **Choose Query Method:** You will be asked if you want to use a pre-filled example query or build your own.
6.  **Build Your Query (if not using the example):**
    -   You will be guided step-by-step to input each parameter of your query.
    -   Each prompt will show a default value taken from a pre-defined example. You can press **Enter** to accept the default or type your own value.

Once the setup is complete, a status animation will show the agent's progress. Finally, the agent will process your query and either print the structured report to the console or save it to the specified file.

### Non-Interactive Usage (with Environment Variables)

While the interactive setup is recommended, you can still pre-configure the agent by setting environment variables in a `.env` file. If you do this, you might want to modify `main.py` to bypass the interactive prompts.

## Extending the Agent

-   **Adding New Agents:** You can create new agent modules within `src/aweagent/agents/` and integrate them into the `PaperAgent` workflow in `src/aweagent/workflow.py`.
-   **Modifying Tools:** The `tool.py` file can be extended with new functions to interact with other APIs or data sources.
-   **Customizing Reporting:** The `reporter.py` agent can be modified to generate reports in different formats or with different content. 