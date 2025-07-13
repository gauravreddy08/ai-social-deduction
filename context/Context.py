import asyncio
from datetime import datetime, timedelta
from logger_config import get_logger

class Context:
    _instance = None
    _initialized = False
    
    def __new__(cls, game_name: str = "game"):
        if cls._instance is None:
            cls._instance = super(Context, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, game_name: str = "game"):
        if not Context._initialized:
            self.messages = ""
            self.buffer = set()
            self.lock = asyncio.Lock()
            self.game_name = game_name
            Context._initialized = True
            self.logger = get_logger('context', game_name=game_name)

    async def add_message(self, from_user: str, message: str) -> None:
        timestamp = self._get_timestamp()
        formatted_message = f"[{timestamp}] {from_user}: {message}"
        print(formatted_message)  # Print to console
        self.logger.info(f"{from_user}: {message}")
        async with self.lock:    
            self.messages += formatted_message + "\n"
            if from_user in self.buffer:
                self.buffer.remove(from_user)

    async def add_typing(self, from_user: str) -> None:
        async with self.lock:
            self.buffer.add(from_user)
        # Don't print typing indicators, just log them
        self.logger.debug(f"{from_user} is typing...")
    
    def _get_timestamp(self) -> str:
        return datetime.now().strftime("%H:%M:%S")
    
    async def get_context(self) -> str:
        async with self.lock:
            context = self.messages
            for user in self.buffer:
                context += f"[{self._get_timestamp()}] {user} is typing...\n"
            return context
    
    async def start_round(self, round_num: int, round_duration: int, players: list[str]) -> None:
        async with self.lock:
            timestamp = self._get_timestamp()
            end_time = (datetime.now() + timedelta(minutes=round_duration)).strftime('%H:%M:%S')
            
            # Print round info
            print(f"[{timestamp}] Round {round_num} has started! Round will end at {end_time}")
            print(f"[{timestamp}] Players Alive: {players}")
            
            self.logger.info(f"Round {round_num} started! Duration: {round_duration} minutes")
            self.logger.info(f"Players alive: {players}")
            
            content = f"[{timestamp}] Round {round_num} has started! Round will end at {end_time}\n"
            content += f"[{timestamp}] Players Alive: {players}\n"
            self.messages += content
            self.buffer = set()

async def main():
    pass

if __name__ == "__main__":
    asyncio.run(main())