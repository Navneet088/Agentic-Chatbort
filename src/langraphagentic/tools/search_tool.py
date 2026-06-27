import os
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import ToolNode 

def get_tool():
    """
    Returns verified tool objects to be used in the chatbot.
    Includes environment variable lookup safety checks.
    """
    # 1. Grab key safely from current session environment
    tavily_api_key = os.environ.get("TAVILY_API_KEY", "").strip()
    
    # 2. Guardrail: If key doesn't exist, log an explicit warning 
    # instead of crashing the initialization instantly
    if not tavily_api_key:
        print("⚠️ Warning: TAVILY_API_KEY environment variable is missing!")
        # Fallback to default loading structure (looks for standard system environment)
        return [TavilySearchResults(max_results=2)]
        
    # Explicit constructor passing is much more robust
    tools = [TavilySearchResults(max_results=2, api_key=tavily_api_key)]
    return tools

def create_tool_node(tools):
    """
    Creates and returns a ToolNode for the LangGraph framework execution pipeline.
    """
    if not tools:
        # Fallback check to avoid passing empty lists to ToolNode runtime engine
        raise ValueError("Cannot create a ToolNode with an empty list of tools.")
        
    return ToolNode(tools=tools)