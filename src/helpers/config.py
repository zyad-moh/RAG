from pydantic_settings import BaseSettings, SettingsConfigDict

class settings(BaseSettings):
    APP_NAME: str # that ia the app_name which inside ".env"
    APP_VERSION: str
    OPENAI_API_KEY: str

    class Config():# path of .env, any thing in ".env" will be loaded and i will able to use it(data configration for validation)
        env_file=".env"

def get_settings(): 
    return settings()