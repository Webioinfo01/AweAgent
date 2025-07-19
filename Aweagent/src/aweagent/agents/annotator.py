from agno.agent import Agent
from textwrap import dedent
from pydantic import BaseModel, Field

class PaperModel(BaseModel):
    doi: str = Field(description="The paper DOI")
    domain: str = Field(description="The research domain of the paper")
    category: str = Field(description="The category of the paper")


class PaperListModel(BaseModel):
    paper_list: list[PaperModel] = Field(description="The list of papers")
    category_list: list[str] = Field(description="The list of categories")


def create_annotator_agent(model):
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
    return annotator 