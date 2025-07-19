from agno.agent import Agent
from textwrap import dedent
from ..tool import search_papers

def create_searcher_agent(model, semanticscholar_api_key: str | None = None):

    def search_semantic_scholar_papers(query: str, publication_date_or_year: str | None = None):
        """
        Search for papers from the Semantic Scholar.
        
        Args:
            query (str): Plain-text search query string. don't be confused with the predefined category list.
            publication_date_or_year (str, optional): "start_date:end_date", "start_date:" or ":end_date", where dates are in the format YYYY-MM-DD, YYYY-MM, or YYYY.
        """
        return search_papers(
            query=query,
            publication_date_or_year=publication_date_or_year,
            semanticscholar_api_key=semanticscholar_api_key
        )

    searcher = Agent(
        name="searcher",
        model=model,
        description="Paper search",
        tools=[search_semantic_scholar_papers],
        instructions=dedent("""
            You are a paper search agent. you need to search the paper from the Semantic Scholar.
            return full output from tool calling.
            if the paper is not found, return an empty list.
            
            Tool calling specification:
            - search_semantic_scholar_papers:
                - query (str): Plain-text search query string. don't be confused with the predefined category list.
                - publication_date_or_year: "start_date:end_date", "start_date:" or ":end_date", where dates are in the format YYYY-MM-DD, YYYY-MM, or YYYY	
            
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
    return searcher 