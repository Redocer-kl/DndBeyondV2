import os

class Settings:
    BROKER_URL: str = os.getenv("BROKER_URL", "amqp://guest:guest@localhost:5672//")
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "gemma2:9b")

settings = Settings()