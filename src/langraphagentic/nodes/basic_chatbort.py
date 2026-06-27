from src.langraphagentic.state.state import State



class BasicChatbort:
    """Basic Chatbort logic Impliment """
    def __init__(self, model):
        self.llm=model
    def process_input(self,state:State)->dict:
        """
        Process user input and generate a response using the LLM model.
        """
        return {"messages":self.llm.invoke(state['messages'])}