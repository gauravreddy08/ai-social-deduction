from game.mafia.controller import Game
from logger_config import setup_logging
import asyncio

game_name = "mafia"
logger = setup_logging(game_name=game_name)
game = Game(n_players=5)
logger.debug(f"{game_name} Game Starting...")

asyncio.run(game.start_game())

logger.debug("Game finished!")
