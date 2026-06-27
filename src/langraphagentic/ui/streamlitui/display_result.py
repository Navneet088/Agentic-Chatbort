import os  
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

class DisplayResultStreamlit:
    def __init__(self, usecase, graph, user_message):
        self.usecase = usecase
        self.graph = graph
        self.user_message = user_message

    def display_result_on_ui(self):
        usecase = self.usecase
        graph = self.graph
        user_message = self.user_message
        
        # --- 1. USECASE: BASIC CHATBOT ---
        if usecase in ["Basic Chatbot", "Basic Chatbort"]:
            with st.chat_message("assistant", avatar="🤖"):
                response_placeholder = st.empty()
                full_response = ""
                
                for event in graph.stream({'messages': [("user", user_message)]}):
                    for value in event.values():
                        if "messages" in value:
                            msg = value["messages"]
                            
                            if isinstance(msg, AIMessage):
                                full_response += msg.content
                                response_placeholder.markdown(full_response + "▌")
                            elif isinstance(msg, list) and len(msg) > 0 and isinstance(msg[-1], AIMessage):
                                full_response += msg[-1].content
                                response_placeholder.markdown(full_response + "▌")
                
                if full_response:
                    response_placeholder.markdown(full_response)
                    st.session_state.chat_history.append({"role": "assistant", "content": full_response})
                    
        # --- 2. USECASE: CHATBOT WITH WEB ---
        elif usecase == "Chatbot With Web":
            initial_state = {"messages": [("user", user_message)]}
            res = graph.invoke(initial_state)
            
            for message in res.get("messages", []):
                if isinstance(message, HumanMessage):
                    continue
                
                elif isinstance(message, ToolMessage):
                    with st.expander("🔍 Web Search Execution Logs", expanded=False):
                        st.caption("**Retrieved Intelligence Matrix Data:**")
                        st.write(message.content)
                        
                elif isinstance(message, AIMessage) and message.content:
                    with st.chat_message("assistant", avatar="🌐"):
                        st.write(message.content)
                    
                    st.session_state.chat_history.append({"role": "assistant", "content": message.content})
        
        # --- 3. USECASE: AI NEWS MANAGEMENT ---
        elif usecase == "AI News":
            clean_input = str(user_message).strip().lower()
            
            frequency = None
            for timeframe in ['daily', 'weekly', 'monthly', 'year']:
                if timeframe in clean_input:
                    frequency = timeframe
                    break
            
            if not frequency:
                st.warning("⚠️ Clear frequency configuration target missing.")
            else:
                with st.spinner(f"🔄 Compiling comprehensive AI news matrix... Please wait."):
                    try: 
                        graph_output = graph.invoke({"messages": [("user", frequency)]})
                        graph_summary = graph_output.get('summary')
                        
                        current_dir = os.path.dirname(os.path.abspath(__file__))
                        project_root = current_dir.split("src")[0] if "src" in current_dir else current_dir
                        ai_news_file_path = os.path.join(project_root, "AINews", f"{frequency}_summary.md")
                        
                        markdown_content = ""
                        if os.path.exists(ai_news_file_path):
                            with open(ai_news_file_path, "r", encoding="utf-8") as file:
                                markdown_content = file.read()
                        elif graph_summary and graph_summary != "No active data blocks available to summarize.":
                            markdown_content = graph_summary
                        
                        if markdown_content:
                            with st.container(border=True):
                                st.markdown(markdown_content)
                            st.session_state.chat_history.append({"role": "assistant", "content": markdown_content})
                        else:
                            st.error("❌ State tracking lost.")
                    except Exception as system_error:
                        st.error(f"❌ Core Error: {str(system_error)}")
        
        # --- 4. USECASE: BLOG GENERATOR ---
        elif usecase == "Blog Generator":
            with st.spinner("✍️ Writing publication-ready technical blog... Please wait."):
                try:
                    graph_output = graph.invoke({"messages": [("user", user_message)]})
                    blog_text = graph_output.get('blog_content')
                    
                    if not blog_text and graph_output.get('blog'):
                        blog_obj = graph_output.get('blog')
                        if hasattr(blog_obj, 'title') and hasattr(blog_obj, 'content'):
                            blog_text = f"# {blog_obj.title}\n\n{blog_obj.content}"
                        elif isinstance(blog_obj, dict):
                            blog_text = f"# {blog_obj.get('title', '')}\n\n{blog_obj.get('content', '')}"
                    
                    if blog_text:
                        # Clean and elegant standard container
                        with st.container(border=True):
                            st.markdown(blog_text)
                        
                        st.session_state.chat_history.append({"role": "assistant", "content": blog_text})
                        st.markdown("<br>", unsafe_allow_html=True) # <-- Sahi argument update kar diya hai
                        st.download_button("📥 Export Production Blog (.md)", data=blog_text, file_name="generated_blog.md", use_container_width=True)
                    else:
                        st.error("⚠️ State sync failed: No content returned.")
                except Exception as e:
                    st.error(f"❌ Execution Error inside Blog Chain: {str(e)}")