from game.mafia.controller import Game
from logger_config import setup_logging
import asyncio

# Initialize logging system with game name
GAME_NAME = "mafia"  # Can be changed to any other game name
logger = setup_logging(game_name=GAME_NAME)
logger.info(f"{GAME_NAME.title()} Game Starting...")

# Create and run game
game = Game(n_players=5)
asyncio.run(game.start_game())

logger.info("Game finished!")
