from src.langraphagentic.state.state import State
from langchain_core.messages import AIMessage

class ChatbotWithtoolsNode:
    """
    ChatbotWithtoolsNode handles the initialization and processing 
    for an LLM that utilizes external tools.
    """
    def __init__(self, model):
        self.llm = model
    
    def process_input(self, state: State) -> dict:
        """
        Main default processing endpoint using the complete message history.
        Safe fallback if called directly by a basic state node runner.
        """
        # Safe extraction of the entire state message list
        messages_history = state.get("messages", [])
        if not messages_history:
            return {"messages": []}
            
        # Invoke the base model with full context history instead of a single string
        llm_response = self.llm.invoke(messages_history)
        return {"messages": [llm_response]}
    
    def create_chatbot(self, tools):
        """
        Dynamically binds external tools to the LLM and returns a functional 
        node closure that integrates cleanly with langgraph's tools_condition.
        """
        # Secure tool binding setup
        llm_with_tools = self.llm.bind_tools(tools)

        def chatbot_node(state: State):
            # Fetch complete conversational state history
            messages_history = state.get("messages", [])
            if not messages_history:
                return {"messages": []}
                
            # Executes the tool-aware model across the entire text history pipeline
            response = llm_with_tools.invoke(messages_history)
            return {"messages": [response]}
            
        return chatbot_node