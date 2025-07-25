"""
Logging Configuration Utilities

This module provides logging configuration and utilities for the Data Protection AI Assistant.

Author: Adryan R A
"""

import logging
import logging.config
import sys
from pathlib import Path
from typing import Optional

from ..core.config import settings


def setup_logging(log_file: Optional[str] = None) -> None:
    """
    Set up logging configuration for the application.
    
    Args:
        log_file (Optional[str]): Path to log file. If None, logs only to console.
    """
    
    log_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'detailed': {
                'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'level': settings.LOG_LEVEL,
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'stream': sys.stdout
            }
        },
        'loggers': {
            'src': {
                'level': settings.LOG_LEVEL,
                'handlers': ['console'],
                'propagate': False
            },
            'langchain': {
                'level': 'WARNING',
                'handlers': ['console'],
                'propagate': False
            },
            'elasticsearch': {
                'level': 'WARNING', 
                'handlers': ['console'],
                'propagate': False
            }
        },
        'root': {
            'level': settings.LOG_LEVEL,
            'handlers': ['console']
        }
    }
    
    # Add file handler if log_file is specified
    if log_file:
        # Create logs directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        log_config['handlers']['file'] = {
            'level': settings.LOG_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'detailed',
            'filename': log_file,
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        }
        
        # Add file handler to all loggers
        for logger_name in log_config['loggers']:
            log_config['loggers'][logger_name]['handlers'].append('file')
        log_config['root']['handlers'].append('file')
    
    logging.config.dictConfig(log_config)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name (str): Logger name
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)
