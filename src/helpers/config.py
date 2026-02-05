from pydantic_settings import BaseSettings, SettingsConfigDict

class settings(BaseSettings):
    APP_NAME: str # that ia the app_name which inside ".env"
    APP_VERSION: str
    OPENAI_API_KEY: str
    FILE_ALLOWED_TYPES:list
    FILE_MAX_SIZE:int 
    FILE_DEFULT_CHUNK_SIZE:int
    MONGODB_URL: str
    MONGODB_DATABASE: str    
    MONGODB_URL: str
    MONGODB_DATABASE: str

    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str

    OPENAI_API_KEY: str = None
    OPENAI_API_URL: str = None
    COHERE_API_KEY: str = None

    GENERATION_MODEL_ID: str = None
    EMBEDDING_MODEL_ID: str = None
    EMBEDDING_MODEL_SIZE: int = None
    INPUT_DAFAULT_MAX_CHARACTERS: int = None
    GENERATION_DAFAULT_MAX_TOKENS: int = None
    GENERATION_DAFAULT_TEMPERATURE: float = None
    
    VECTOR_DB_BAKEND : str 
    VECTOR_DB_PATH : str 
    VECTOR_DB_DISTANCE_METHOD : str = None
    
    
    
    class Config():# path of .env, any thing in ".env" will be loaded and i will able to use it(data configration for validation)
        env_file=".env"

def get_settings(): 
    return settings()