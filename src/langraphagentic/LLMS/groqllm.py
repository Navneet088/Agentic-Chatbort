import os
import streamlit as st
from langchain_groq import ChatGroq


class GroqLLm:
    def __init__(self, user_control_input):
        self.user_control_input = user_control_input
    
    def get_llm_model(self):
        try:
            # 1. Grab values safely with fallback defaults
            groq_api_key = self.user_control_input.get("GROQ_API_KEY", "").strip()
            selected_groq_model = self.user_control_input.get("selected_groq_model")
            
            # 2. Check environment variables if the user UI field is blank
            if not groq_api_key:
                groq_api_key = os.environ.get("GROQ_API_KEY", "").strip()

            # 3. Halt processing immediately if no API key is found
            if not groq_api_key:
                st.error("⚠️ GROQ API key is missing. Please provide a valid API key in the sidebar.")
                return None
            
            if not selected_groq_model:
                st.error("⚠️ No Groq model selected. Please choose a model from the dropdown.")
                return None
            
            # 4. Safely initialize and return the model instance
            llm = ChatGroq(api_key=groq_api_key, model=selected_groq_model)
            return llm
        
        except Exception as e:
            st.error(f"Failed to initialize the model: {e}")
            return None