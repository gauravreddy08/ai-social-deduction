import logging
import logging.handlers
from datetime import datetime
import os

def setup_logging(game_name="game", log_dir="logs"):
    """
    Set up centralized logging configuration for any game.
    
    Args:
        game_name: Name of the game for logger naming (default: "game")
        log_dir: Directory to store log files (default: "logs")
    
    Creates both console and file handlers with appropriate formatting.
    Returns the configured logger instance.
    """
    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Create logger with the game name
    logger = logging.getLogger(game_name)
    logger.setLevel(logging.DEBUG)
    
    # Remove any existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter('%(message)s')
    
    simple_formatter = logging.Formatter('%(message)s')
    
    # Console handler (INFO and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # File handler (DEBUG and above) - creates a new file for each session
    log_filename = os.path.join(log_dir, f'{game_name}_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    file_handler = logging.FileHandler(log_filename, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Also configure module-specific loggers
    for module_name in ['controller', 'context', 'player', 'agent']:
        module_logger = logging.getLogger(f'{game_name}.{module_name}')
        module_logger.setLevel(logging.DEBUG)
    
    # Store the game name for get_logger to use
    logger.game_name = game_name
    
    return logger

def get_logger(module_name=None, game_name="game"):
    """
    Get a logger instance for a specific module.
    
    Args:
        module_name: Name of the module (e.g., 'controller', 'context')
                    If None, returns the main logger
        game_name: Name of the game (should match what was used in setup_logging)
    
    Returns:
        Logger instance
    """
    if module_name:
        return logging.getLogger(f'{game_name}.{module_name}')
    return logging.getLogger(game_name) 