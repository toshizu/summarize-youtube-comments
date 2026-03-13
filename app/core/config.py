from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gemini_api_key: str
    youtube_api_key: str
    # google_cloud_location: str
    # google_cloud_project: str = "your-project-id"
    
    class Config:
        env_file = ".env"  # 正規のコード
        
settings = Settings()