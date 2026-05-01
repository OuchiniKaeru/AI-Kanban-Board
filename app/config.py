from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "AI Kanban Board"
    debug: bool = True
    database_url: str = "sqlite:///./kanban.db"
    
    # AI Provider Settings
    openai_api_key: str = ""
    openai_model: str = "gpt-5.4-mini"
    
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-4.5-haiku"
    
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    
    # Gemini Settings
    gemini_api_key: str = ""
    gemini_model: str = "gemini-flash-latest"
    
    # OpenRouter Settings
    openrouter_api_key: str = ""
    openrouter_model: str = "openai/gpt-5.4-mini"
    
    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
