from pydantic_settings import BaseSettings, SettingsConfigDict

class settings(BaseSettings):
    APP_NAME: str # that ia the app_name which inside ".env"
    APP_VERSION: str
    OPENAI_API_KEY: str
    FILE_ALLOWED_TYPES:list
    FILE_MAX_SIZE:int 
    FILE_DEFULT_CHUNK_SIZE:int
    class Config():# path of .env, any thing in ".env" will be loaded and i will able to use it(data configration for validation)
        env_file=".env"

def get_settings(): 
    return settings()