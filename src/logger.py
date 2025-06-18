import logging
import sys
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name):
    """
    Config and returns a logger with the specified name.
    Args:
        name (str): Name of the logger

    Returns:
        logging.Logger: Configured logger
    """
    # Create the logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Prevent propagation to root logger to avoid duplicates
    logger.propagate = False

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Create the logs directory if it doesn't exist
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure the format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Handler for console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler for file
    file_handler = RotatingFileHandler(
        filename=os.path.join(log_dir, 'padelbot.log'),
        maxBytes=1024 * 1024,  # 1MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger 