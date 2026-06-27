import streamlit as st
from src.langraphagentic.ui.streamlitui.loadui import LoadStreamlitUI
from src.langraphagentic.LLMS.groqllm import GroqLLm
from src.langraphagentic.graph.graph_builder import Graphbuilder
from src.langraphagentic.ui.streamlitui.display_result import DisplayResultStreamlit

def load_streamlit_ui():
    # --- Initialize chat history if it doesn't exist ---
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    ui_loader = LoadStreamlitUI()
    user_input = ui_loader.load_streamlit_ui()
    
    if not user_input:
        st.error("User input is not available. Please check the UI configuration.")
        return

    # Render past chat history to keep layout persistent above the inputs
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

  
    chat_input_val = st.chat_input("Type your message here...")
    
    # Check if input comes from Fetch Button or normal Text Input Box
    if st.session_state.get("IsFetchButtonClicked", False):
        user_messages = st.session_state.get("timeframe", None)
        # Reset the state so it doesn't loop infinitely on next re-run
        st.session_state.IsFetchButtonClicked = False 
    else:
        user_messages = chat_input_val

    # Execution Flow Trigger
    if user_messages:
        # Display user message instantly and commit to state history
        with st.chat_message("user"):
            st.write(user_messages)

        st.session_state.chat_history.append({"role": "user", "content": user_messages})
        
        try:
            # Initialize LLM Pipeline
            obj_llm_config = GroqLLm(user_control_input=user_input)
            model = obj_llm_config.get_llm_model()

            if not model:
                st.error("Model is not available. Please check the LLM configuration.")
                return
                
            usecase = user_input.get("selected_usecase")
            if not usecase:
                st.error("Use case is not selected. Please select a use case.")
                return
                
            # Build and execute Agent StateGraph
            graph_builder = Graphbuilder(model)
            try:
                graph = graph_builder.setup_graph(usecase)
                
                # Executing display result wrapper class
                display_handler = DisplayResultStreamlit(usecase, graph, user_messages)
                display_handler.display_result_on_ui()
                
            except Exception as graph_err:
                st.error(f"❌ Graph Setup Failed: {str(graph_err)}")
                return    

        except Exception as system_err:
            # FIX 2: Streamlit safe error output instead of crushing server via raw raise execution
            st.error(f"💥 Configuration Exception Encountered: {str(system_err)}")