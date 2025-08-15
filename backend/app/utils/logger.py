import logging
from typing import Optional
from app.core.config import settings

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        
        if settings.debug:
            logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        else:
            logger.setLevel(logging.INFO)
            formatter = logging.Formatter(
                "%(levelname)s - %(message)s"
            )
        
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False
    
    return logger

def setup_logging():
    root_logger = logging.getLogger()
    
    root_logger.handlers.clear()
    
    if settings.debug:
        root_logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.INFO)