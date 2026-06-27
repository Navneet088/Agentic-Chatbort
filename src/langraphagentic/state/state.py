from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from typing import Annotated, List, Optional
from pydantic import BaseModel, Field

class Blog(BaseModel):
    title: str = Field(description="The title of the blog post")
    content: str = Field(description="The main content of the blog post")

class State(TypedDict):
    """
    Represent the structure of the state used in graph
    """
    messages: Annotated[list, add_messages]
    
    # AI News Pipeline Keys
    frequency: str
    news_data: List[dict]
    summary: str
    filename: str
    
    # Blog Generator Pipeline Keys
    topic: str
    blog: Optional[Blog] 
    current_language: str