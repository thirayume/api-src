from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    DRIVER_1: str
    USERNAME_1: str
    PSSWD_1: str
    SERVERNAME_1: str
    DBNAME_1: str

    DRIVER_2: str
    USERNAME_2: str
    PSSWD_2: str
    SERVERNAME_2: str
    DBNAME_2: str

    SECRET_1: str
    ALGORITHM_1: str

    class Config:
        env_file = ".env.sample"


# New decorator for cache
@lru_cache()
def get_settings():
    return Settings()


# Function to update a specific environment variable at runtime
def update_env_variable(key: str, value: str):
    os.environ[key] = value

    with open(".env.sample", "r") as file:
        lines = file.readlines()

    with open(".env.sample", "w") as file:
        for line in lines:
            if line.startswith(f"{key}="):
                file.write(f"{key}={value}\n")
            else:
                file.write(line)

    get_settings.cache_clear()
