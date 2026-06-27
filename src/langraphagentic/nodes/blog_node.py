from langchain_core.prompts import ChatPromptTemplate
from src.langraphagentic.state.state import Blog,State
import os

class BlogNode:
    def __init__(self, llm):
        self.llm = llm

    def generate_title(self, state: dict) -> dict:
        """Node 1: User input se ek catchy headline/title generate karna"""
        try:
            msg = state.get('messages', [])[-1]
            topic = msg.content if hasattr(msg, 'content') else str(msg)
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a creative copywriter. Generate a single catchy headline/title for a blog post based on the topic. Return ONLY the title text, no quotes or introductions."),
                ("user", "Topic: {topic}")
            ])
            res = self.llm.invoke(prompt.invoke({"topic": topic}))
            return {"topic": topic, "blog_title": res.content.strip().replace('"', '')}
        except Exception as e:
            return {"topic": "Agentic AI", "blog_title": "The Rise of Agentic AI"}

    def generate_content(self, state: dict) -> dict:
        """Node 2: Full structured blog content generate karna aur Pydantic object banana"""
        title = state.get('blog_title', 'Agentic AI')
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert technical blogger. Write a comprehensive, high-quality professional blog post using strict Markdown format based on the given title. Include headings, body points, and a professional conclusion."),
            ("user", "Write a structured blog post for the title: {title}")
        ])
        res = self.llm.invoke(prompt.invoke({"title": title}))
        
        # --- FIXED: Pydantic Object Mapping ---
        blog_object = Blog(title=title, content=res.content)
        return {"blog_content": f"# {title}\n\n{res.content}", "blog": blog_object}

    def save_blog(self, state: dict) -> dict:
        """Node 3: File ko disk par cleanly save karna"""
        content = state.get('blog_content', '')
        root = os.path.dirname(os.path.abspath(__file__)).split("src")[0]
        target_dir = os.path.join(root, "GeneratedBlogs")
        os.makedirs(target_dir, exist_ok=True)
        
        clean_name = "".join([c if c.isalnum() else "_" for c in state.get('blog_title', 'blog')])[:20]
        path = os.path.join(target_dir, f"{clean_name}.md")
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"filename": path}