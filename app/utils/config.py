from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DRIVER: str
    USERNAME: str
    PSSWD: str
    SERVERNAME: str
    INSTANCENAME: str
    DB: str

    class Config:
        env_file = ".env.sample"


# New decorator for cache
@lru_cache()
def get_settings():
    return Settings()
