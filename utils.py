# Utility functions for the game

def display(message: str, logger=None):
    """
    Display a message to console and optionally log it.
    
    Args:
        message: The message to display
        logger: Optional logger instance to also log the message
    """
    print(message)
    if logger:
        logger.info(message)