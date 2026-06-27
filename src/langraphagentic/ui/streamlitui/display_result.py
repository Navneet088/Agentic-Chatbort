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
                        st.markdown(message.content)
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
                with st.spinner("🔄 Compiling comprehensive AI news matrix... Please wait."):
                    try: 
                        # Direct state transmission channel
                        graph_output = graph.invoke({"messages": [("user", frequency)]})
                        
                        # --- 🎯 FIXED: NO HARD DRIVE FILE READS ---
                        # State dictionary ya last output context se seedhe data nikalna
                        markdown_content = graph_output.get('summary', '')
                        
                        if not markdown_content and "messages" in graph_output and graph_output["messages"]:
                            last_msg = graph_output["messages"][-1]
                            if hasattr(last_msg, 'content'): 
                                markdown_content = last_msg.content

                        if markdown_content and markdown_content != "No active data blocks available to summarize.":
                            with st.container(border=True):
                                st.markdown(markdown_content)
                            st.session_state.chat_history.append({"role": "assistant", "content": markdown_content})
                        else:
                            st.error("❌ State tracking lost or empty data block returned.")
                    except Exception as system_error:
                        st.error(f"❌ Core Error: {str(system_error)}")
        
        # --- 4. USECASE: BLOG GENERATOR ---
        elif usecase == "Blog Generator":
            with st.spinner("✍️ Writing technical publication via Groq Matrix..."):
                try:
                    # --- 🎯 FIXED: Changed 'active_graph' to 'graph' to fix NameError ---
                    res = graph.invoke({"messages": [("user", user_message)]})
                    blog_text = res.get("blog_content", "")
                    
                    # Fallback resolution layer if key structural mismatch happens
                    if not blog_text and res.get("blog"):
                        blog_obj = res.get("blog")
                        if hasattr(blog_obj, 'content'):
                            blog_text = blog_obj.content
                    
                    if blog_text:
                        with st.chat_message("assistant", avatar="📝"):
                            st.markdown(blog_text)
                        st.session_state.chat_history.append({"role": "assistant", "content": blog_text})
                        
                        st.download_button(
                            "📥 Download Blog (.md)", 
                            data=blog_text, 
                            file_name="generated_blog.md", 
                            use_container_width=True
                        )
                    else:
                        st.error("⚠️ Failed to extract blog layout metadata structure from state.")
                except Exception as blog_error:
                    st.error(f"❌ Execution Error inside Blog Chain: {str(blog_error)}")