from typing import Optional
from functools import lru_cache
from pydantic import BaseSettings


class BaseConfig(BaseSettings):
    ENV_STATE: str = None
    class Config:
        env_file = ".env"
        
class GlobalConfig(BaseConfig):
    DATABASE_URL: Optional[str] = None
    DB_FORCE_ROLL_BACK: bool = False
    
class DevConfig(GlobalConfig):
    class Config:
        env_prefix = "DEV_"
        
class ProdConfig(GlobalConfig):
    class Config:
        env_prefix = 'PROD_'
        
class TestConfig(GlobalConfig):
    DATABASE_URL: str = "sqlite:///./test.db"
    DB_FORCE_ROLL_BACK: bool = True
    class Config:
        env_prefix = 'TEST_'
        
@lru_cache()
def get_config(env_state:str):
    configs = {"dev": DevConfig, "prod": ProdConfig, "test": TestConfig}
    return configs[env_state]()

config = get_config(BaseConfig().ENV_STATE)