from langgraph.graph import StateGraph, START, END
from src.langraphagentic.state.state import State,Blog
from src.langraphagentic.nodes.basic_chatbort import BasicChatbort
from src.langraphagentic.tools.search_tool import get_tool, create_tool_node
from langgraph.prebuilt import tools_condition
from src.langraphagentic.nodes.chatbot_with_tools_node import ChatbotWithtoolsNode
from src.langraphagentic.nodes.ai_news_node import AiNewsNode
from src.langraphagentic.nodes.blog_node import BlogNode

class Graphbuilder:
    def __init__(self, model):
        self.llm = model
        

    def basic_chatbot_graph(self):
        """Build a basic chatbot graph using langgraph."""
        # Initialize a fresh local workflow instance
        workflow = StateGraph(State)
        
        basic_chatbot_node = BasicChatbort(self.llm)
        workflow.add_node("Basic_Chatbot", basic_chatbot_node.process_input)
     
        workflow.add_edge(START, "Basic_Chatbot")
        workflow.add_edge("Basic_Chatbot", END)
        
        return workflow.compile()
    
    def chatbot_with_tools_build_graph(self):
        """Build a chatbot graph with dynamic web tool integrations."""
        # Initialize a fresh local workflow instance
        workflow = StateGraph(State)
        
        tools = get_tool()
        tool_node = create_tool_node(tools)
        
        obj_chatbot_with_node = ChatbotWithtoolsNode(self.llm)
        chabot_node = obj_chatbot_with_node.create_chatbot(tools)

        workflow.add_node("Chatbot", chabot_node)
        workflow.add_node("tools", tool_node)

        workflow.add_edge(START, "Chatbot")
        
        workflow.add_conditional_edges(
            "Chatbot",
            tools_condition,
            {
                "tools": "tools",
                "__end__": END
            }
        )
        workflow.add_edge("tools", "Chatbot")
        
        return workflow.compile()
        
    def ai_news_builder_graph(self):
        """Build a sequential pipeline for scraping and summarizing AI news."""
        
        workflow = StateGraph(State)
        
        ai_news_node = AiNewsNode(self.llm)

        # Nodes Register
        workflow.add_node("fetch_news", ai_news_node.fetch_news)
        workflow.add_node("summarize_news", ai_news_node.summarize_news)
        workflow.add_node("save_result", ai_news_node.save_result)

        # Strict Execution Flow Setup
        workflow.add_edge(START, "fetch_news") 
        workflow.add_edge("fetch_news", "summarize_news")
        workflow.add_edge("summarize_news", "save_result")
        workflow.add_edge("save_result", END)
        
        return workflow.compile()

    def blog_generator_graph(self):
            """Build a sequential pipeline for blog title and content generation."""
            workflow = StateGraph(State)
            blog_node = BlogNode(self.llm)

            # Nodes Registration
            workflow.add_node("generate_title", blog_node.generate_title)
            workflow.add_node("generate_content", blog_node.generate_content)
            workflow.add_node("save_blog", blog_node.save_blog)

            # Execution Flow Set
            workflow.add_edge(START, "generate_title")
            workflow.add_edge("generate_title", "generate_content")
            workflow.add_edge("generate_content", "save_blog")
            workflow.add_edge("save_blog", END)
            
            return workflow.compile()    

    def setup_graph(self, usecase: str):
        """Sets up and compiles the graph for the selected use case dynamically without state collisions."""
        
        if usecase in ["Basic Chatbot", "Basic Chatbort"]:
            return self.basic_chatbot_graph()
            
        elif usecase == "Chatbot With Web":
            return self.chatbot_with_tools_build_graph()
            
        elif usecase == "AI News":
            return self.ai_news_builder_graph()
        elif usecase == "Blog Generator":
            return self.blog_generator_graph()
            
        else:
            raise ValueError(f"Unknown usecase requested: {usecase}")