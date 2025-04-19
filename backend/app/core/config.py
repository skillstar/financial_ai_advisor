import os  
from pydantic_settings import BaseSettings  
from typing import Optional  
from functools import lru_cache  

class Settings(BaseSettings):  
    # 环境设置  
    ENVIRONMENT: str = "development"  
    
    # API配置  
    API_HOST: str = "0.0.0.0"  
    API_PORT: int = 8000  
    DEBUG: bool = True  
    
    # 数据库配置  
    DB_USER: str = "root"  
    DB_PASSWORD: str  
    DB_HOST: str = "localhost"  
    DB_PORT: int = 3306  
    DB_NAME: str = "crewai_financial"  
    DATABASE_URL: str  
    
    # Redis 配置  
    REDIS_URL: str = "redis://localhost:6379/0"  
    
    # LLM配置  
    LLM_PROVIDER: str = "deepseek"  
    LLM_MODEL: str = "deepseek-chat"  
    LLM_TEMPERATURE: float = 0.7  
    LLM_MAX_TOKENS: int = 500  
    
    # Deepseek 配置  
    DEEPSEEK_API_KEY: str  
    DEEPSEEK_API_BASE: str = "https://api.deepseek.com/v1"  
    
    # GLM 配置 (备用)  
    GLM_API_KEY: Optional[str] = None  
    GLM_API_BASE: Optional[str] = None  
    GLM_EMBEDDING_API_BASE: Optional[str] = None  

    class Config:  
        env_file = ".env"  
        env_file_encoding = "utf-8"  
        case_sensitive = True  

@lru_cache()  
def get_settings():  
    return Settings()  

settings = get_settings()  