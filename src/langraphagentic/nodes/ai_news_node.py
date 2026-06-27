from src.langraphagentic.nodes.chatbot_with_tools_node import ChatbotWithtoolsNode
from tavily import TavilyClient 
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
import os

class AiNewsNode:
    def __init__(self, llm):
        # Initialize directly from global environment values safely
        self.tavily = None
        self.llm = llm

    def fetch_news(self, state: dict) -> dict:
        """Fetch AI news based on the frequency found in the state safely."""  
        # Tavily runtime backup client setup
        if not self.tavily:
            api_key = os.environ.get("TAVILY_API_KEY") or os.getenv("TAVILY_API_KEY")
            if api_key:
                self.tavily = TavilyClient(api_key=api_key)
            else:
                # If key is completely missing, fast-forward with safe fake data gracefully
                return {
                    "frequency": "daily",
                    "news_data": [{"content": "Tavily API key was not injected or missing in environment context.", "url": "#", "published_date": "2026-06-27"}]
                }

        try:
            messages_list = state.get('messages', [])
            if not messages_list:
                return {"frequency": "daily", "news_data": []}
                
            raw_content = messages_list[-1].content
            frequency = str(raw_content).lower().strip()
            
            chosen_frequency = 'daily'
            for timeframe in ['daily', 'weekly', 'monthly', 'year']:
                if timeframe in frequency:
                    chosen_frequency = timeframe
                    break
            
            time_range_map = {'daily': 'd', 'weekly': 'w', 'monthly': 'm', 'year': 'y'}
            days_map = {'daily': 1, 'weekly': 7, 'monthly': 30, 'year': 366}

            tavily_range = time_range_map.get(chosen_frequency, 'd')
            tavily_days = days_map.get(chosen_frequency, 1)

            response = self.tavily.search(
                query="Top Artificial Intelligence (AI) technology news India and globally",
                topic="news",
                time_range=tavily_range,
                include_answer="advanced",
                max_results=10,
                days=tavily_days,
            )

            # --- STANDARD STATE UPDATE RULE ---
            # Return only sliced changes instead of writing into deep local states
            return {
                "frequency": chosen_frequency,
                "news_data": response.get('results', []) or [{"content": "No recent tech articles indexed for this timeframe.", "url": "#", "published_date": "2026-06-27"}]
            }
            
        except Exception as e:
            # Safe Fallback dictionary to force graph to proceed to summarize_news
            return {
                "frequency": "daily",
                "news_data": [{"content": f"Bypassed live query fetch. Pipeline exception trace: {str(e)}", "url": "#", "published_date": "2026-06-27"}]
            }

    def summarize_news(self, state: dict) -> dict:
        """Summarize the fetched news using the LLM."""
        new_items = state.get("news_data", [])
        
        if not new_items:
            return {"summary": "No active data blocks available to summarize."}

        prompt_template = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are an expert AI news summarizer. Your task is to summarize AI news articles into strict markdown format.\n\n"
                "For EACH article, you MUST follow this exact format:\n"
                "### [YYYY-MM-DD]\n"
                "[Concise sentence summary here](URL)\n\n"
                "Rules:\n"
                "1. Convert all timestamps/dates into the YYYY-MM-DD format based on the IST timezone.\n"
                "2. The summary must be a single, concise sentence.\n"
                "3. Do not add any extra text, introduction, or markdown styling outside of the requested format."
            ),
            ("user", "Articles:\n{articles}")
        ])
        
        articles_str = "\n\n".join([
            f"Content: {item.get('content', '')}\nURL: {item.get('url', '')}\nDate: {item.get('published_date', '')}"
            for item in new_items
        ])
        
        prompt_value = prompt_template.invoke({"articles": articles_str})
        response = self.llm.invoke(prompt_value)
        
        return {"summary": response.content}

    def save_result(self, state: dict) -> dict:
        """Saves the generated summary markdown into the filesystem cleanly."""
        frequency = state.get('frequency', 'ai')
        summary = state.get('summary', '')
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if "src" in current_dir:
            project_root = current_dir.split("src")[0]
        else:
            project_root = current_dir

        target_dir = os.path.join(project_root, "AINews")
        os.makedirs(target_dir, exist_ok=True)
        
        filename = os.path.join(target_dir, f"{frequency}_summary.md")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# {frequency.capitalize()} AI News Summary\n\n")
            f.write(summary)
            
        return {"filename": filename}