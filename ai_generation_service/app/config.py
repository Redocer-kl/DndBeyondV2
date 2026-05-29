import os

class Settings:
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "gemma2:9b")

settings = Settings()