from logging.config import dictConfig
from storeapi.config import DevConfig, config
import logging

def obfuscated(email: str, obfuscated_length: int = 2) -> str:
    """Obfuscate an email address by replacing the local part with asterisks."""
    try:
        characters = email[:obfuscated_length]
        first,last = email.split("@")
        return characters + ("*" * (len(first)- obfuscated_length)) + "@" + last
    except ValueError:
        return email
    
    

class EmailObfuscationFilter(logging.Filter):
    def __init__(self,name: str = "", obfuscated_length: int = 2)-> None:
        super().__init__(name)
        self.obfuscated_length = obfuscated_length
        
    def filter(self, record: logging.LogRecord) -> bool:
        if "email" in record.__dict__:
            record.email = obfuscated(record.email, self.obfuscated_length)
        return True

handlers = ["default", "rotating_file"]
if isinstance(config, DevConfig):
    handlers = ["default", "rotating_file"]

def configure_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters":{
                "correlation_id":{
                    "()": "asgi_correlation_id.CorrelationIdFilter",
                    "uuid_length": 8 if isinstance(config,DevConfig) else 32,
                    "default_value": "-"
                },
                "email_obfuscation":{
                    "()": EmailObfuscationFilter,
                    "obfuscated_length": 2 if isinstance(config, DevConfig) else 0,
                    },
            },
            "formatters":{
                "console":{
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                    "format": "(%(correlation_id)s) %(asctime)s.%(msecs)03dZ | %(levelname)-8s | %(name)s:%(lineno)d - %(message)s"
                },
                "file":{
                    "class":"pythonjsonlogger.jsonlogger.JsonFormatter",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                    "format": "%(asctime)s.%(msecs)03dZ  %(levelname)-8s [%(correlation_id)s] %(name)s  %(lineno)d  %(message)s"
                }
            },
            "handlers":{
                "default":{
                    "class":"rich.logging.RichHandler",
                    "level": "DEBUG",
                    "formatter": "console" ,
                    "filters": ["correlation_id", "email_obfuscation"],    
                },
                "rotating_file":{
                    "class":"logging.handlers.RotatingFileHandler",
                    "level": "DEBUG",
                    "formatter": "file",
                    "filename": "storeapi.log",
                    "maxBytes": 10 * 1024 * 1024,  # 10 MB
                    "backupCount": 2, # Keep 2 backup files
                    "encoding": "utf-8",
                    "filters": ["correlation_id", "email_obfuscation"]
                }
            },
            "loggers":{
                "uvicorn": {
                    "handlers": ["default", "rotating_file"],
                    "level": "INFO"
                    },
                "storeapi":{
                    "handlers": handlers,
                    "level": "DEBUG" if isinstance(config, DevConfig) else "INFO",
                    "propagate": False
                },
                "databases":{
                    "handlers": ["default"],
                    "level":"WARNING",
                },
                "aiosqlite":{
                    "handlers": ["default"],
                    "level":"WARNING",
                }
            }
        }
    )