import streamlit as st
import os
from src.langraphagentic.ui.uiconfigfile import Config

class LoadStreamlitUI:
    def __init__(self):
        self.config = Config()
        self.user_controls = {}

    def load_streamlit_ui(self):
        # Fetch the title safely
        raw_title = self.config.get_page_title()
        page_title = raw_title if raw_title is not None else "Agentic Workspace"
        
        # Set up the page config
        st.set_page_config(page_title="⚡ " + page_title, layout="wide")
        
        # --- ⚡ CLEAN & ATTRACTIVE PREMIUM TITLE CSS ---
        st.markdown("""
            <style>
                /* Soft Metallic White Title - Zero AI-generated Gradient vibe */
                .main-title { 
                    font-size: 2.3rem; 
                    font-weight: 700; 
                    color: #f8fafc; /* Professional Off-White */
                    letter-spacing: -0.03em;
                    padding-bottom: 2px;
                    margin-bottom: 0.2rem;
                }
                /* Muted Subtitle */
                .sub-title { 
                    font-size: 1rem; 
                    color: #94a3b8; 
                    margin-bottom: 1.8rem; 
                }
                /* Customized Sidebar Styling Elements */
                div[data-testid="stSidebar"] { 
                    background-color: #111114 !important; 
                    border-right: 1px solid #27272a; 
                }
                /* Premium Action Buttons Accent */
                .stButton>button { 
                    background: linear-gradient(45deg, #4facfe, #00f2fe) !important; 
                    color: white !important; 
                    border: none !important; 
                    border-radius: 6px !important; 
                    font-weight: 600 !important;
                    transition: 0.3s ease !important;
                }
                .stButton>button:hover { 
                    background: linear-gradient(45deg, #00f2fe, #4facfe) !important; 
                    transform: scale(1.01); 
                    box-shadow: 0 4px 15px rgba(0, 242, 254, 0.2);
                }
            </style>
        """, unsafe_allow_html=True)

        # Render styled headers cleanly
        st.markdown(f'<div class="main-title">⚡ {page_title}</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">Design, trace, and execute ultra-responsive stateful agent workflows.</div>', unsafe_allow_html=True)
        
        # --- FIX: Initialize states safely without overwriting them on re-runs ---
        if "timeframe" not in st.session_state:
            st.session_state.timeframe = ''
        if "IsFetchButtonClicked" not in st.session_state:
            st.session_state.IsFetchButtonClicked = False 

        with st.sidebar:
            st.markdown("### ⚙️ Core Configuration")
            st.markdown("---")
            
            # Get options from config safely
            llm_options = self.config.get_llm_options()
            usecase_options = self.config.get_usecase_options()

            # LLM selection
            self.user_controls["selected_llm"] = st.selectbox("🌐 Select LLM Engine", llm_options)

            if self.user_controls["selected_llm"] == 'Groq':
                # Model selection
                model_options = self.config.get_groq_model_options()
                self.user_controls["selected_groq_model"] = st.selectbox("🧠 Select Neural Architecture", model_options)
                
                # Safe state wrapper for API key
                if "GROQ_API_KEY" not in st.session_state:
                    st.session_state["GROQ_API_KEY"] = ""
                self.user_controls["GROQ_API_KEY"] = st.text_input("🔑 Groq API Access Token", value=st.session_state["GROQ_API_KEY"], type="password")
                st.session_state["GROQ_API_KEY"] = self.user_controls["GROQ_API_KEY"]
                
                if not self.user_controls["GROQ_API_KEY"]:
                    st.warning("Missing required LLM authorization tokens.")

            st.markdown("---")
            ## Usecase selection
            self.user_controls["selected_usecase"] = st.selectbox("🎯 Target Agent Workflow", usecase_options)
            
            # Initialize Tavily key to avoid dictionary key errors
            self.user_controls["TAVILY_API_KEY"] = ""
            
            if self.user_controls["selected_usecase"] in ["Chatbot With Web", "AI News"]:
                if "TAVILY_API_KEY" not in st.session_state:
                    st.session_state["TAVILY_API_KEY"] = ""
                
                tavily_input = st.text_input("🔍 Tavily Search Framework Token", value=st.session_state["TAVILY_API_KEY"], type="password")
                os.environ["TAVILY_API_KEY"] = self.user_controls["TAVILY_API_KEY"] = st.session_state["TAVILY_API_KEY"] = tavily_input
                
                if not self.user_controls["TAVILY_API_KEY"]:
                    st.warning("Web indexing system tokens required.")
                
            if self.user_controls["selected_usecase"] == "AI News":
                st.markdown("---")
                st.markdown("### 📰 AI Intelligence News Panel")
                
                time_frame = st.selectbox(
                    "📅 Select Timeline Scope",
                    ["📆 Daily Horizon", "🗓️ Weekly Horizon", "📚 Monthly Horizon"],
                    index=0
                )
                
                # Fetch button implementation
                if st.button("🚀 Stream Engine Data Pipeline", use_container_width=True):
                    st.session_state.IsFetchButtonClicked = True
                    st.session_state.timeframe = time_frame
                    st.rerun()

        return self.user_controls