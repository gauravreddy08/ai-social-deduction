from game.undercover.player import UndercoverPlayer
from context.Context import Context
import asyncio
import random
import time
from game.undercover.prompts import SCHEDULER_INSTRUCTIONS, VOTING_PROMPT, CONTRIBUTE_WORD_PROMPT, GENERATOR_INSTRUCTIONS
from collections import defaultdict
from logger_config import get_logger

config = {
    # "generator_model_name": "litellm/anthropic/claude-sonnet-4-20250514",
    # "scheduler_model_name": "litellm/anthropic/claude-3-5-sonnet-20240620",
    "generator_model_name": "o4-mini", 
    "scheduler_model_name": "gpt-4o-mini",
    "scheduler_instructions": SCHEDULER_INSTRUCTIONS,
    "generator_instructions": GENERATOR_INSTRUCTIONS,
    "voting_instructions": VOTING_PROMPT,
    "contribute_word_instructions": CONTRIBUTE_WORD_PROMPT,
}

def get_word():
    with open('game/undercover/words.txt', 'r') as f:
        words = f.read().splitlines()
    return random.choice(words)

class Game:
    def __init__(self, n_players: int, n_imposters: int, name: str = "undercover", word_file: str = "game/undercover/words.txt", round_duration: int = 1.5):
        self.name = name
        self.n_players = n_players
        self.n_imposters = n_imposters
        self.word_file = word_file
        self.round_duration = round_duration
        self.context_manager = Context(game_name=self.name)
        self.logger = get_logger('controller', game_name=self.name)

        self._init_players(n_players, n_imposters)
    
    def _init_players(self, n_players: int, n_imposters: int):
        self.imposters = set(random.sample(range(n_players), n_imposters)) 
        self.word = self._get_word()
        print(f"\n[HIDDEN INFO] Imposters: {self.imposters}")
        print(f"\n[HIDDEN INFO] The Civilian's word is: {self.word}")
        self.players = dict()
        for i in range(n_players):
            player_details = {
                "name": f"Player {i}",
                "role": "Impostor" if i in self.imposters else "Civilian",
                "word": "BLANK" if i in self.imposters else self.word
            }
            
            self.players[i] = UndercoverPlayer(player_details, config)
    
    def _get_word(self):
        with open(self.word_file, 'r') as f:
            words = f.read().splitlines()
        return random.choice(words)

    async def start_game(self):
        round_num = 1
        # print(f"\n[GAME] Game started with {self.n_players} players")
        # print(f"[GAME] Imposters are Players: {", ".join(map(str, self.imposters))}\n")
        
        self.logger.debug(f"Game started with {self.n_players} players")
        self.logger.debug(f"Imposters are Players: {self.imposters}")
        
        while self.n_players > self.n_imposters:

            round_details = {
                "Round Number": round_num,
                "Number of Imposters": self.n_imposters,
                "Number of Players": self.n_players,
                "Players": list(self.players.keys())
            }

            await self.word_round(round_details)

            await self.discussion_round(round_details)

            is_imposter = await self.voting_round(round_details)
            if is_imposter:
                self.n_imposters -= 1
            else:
                self.n_players -= 1

            round_num += 1

            if self.n_imposters == 0:
                self.logger.debug("Game ended with less players than imposters")
                return
            elif self.n_players < self.n_imposters:
                self.logger.debug("Game ended with more imposters than players")
                return

    
    async def word_round(self, round_details: dict):
        print("\n[GAME] Every Player will say their clue word randomly...")
        player_ids = list(self.players.keys())
        random.shuffle(player_ids)
        self.logger.debug("Every Player will say their clue word...")

        for player_id in player_ids:
            player = self.players[player_id]
            word = await player.contribute_word(round_details=round_details)


    async def discussion_round(self, round_details: dict):
        prev_context = await self.context_manager.get_context()
        await self.context_manager.start_round(round_details['Round Number'], self.round_duration, round_details['Players'])
        
        start_time = time.time()
        duration_seconds = self.round_duration * 60
        player_tasks = [] 
        
        while time.time() - start_time < duration_seconds:   
            current_context = await self.context_manager.get_context()
            
            if current_context != prev_context:
                idle_players = [player for player in self.players.values() if player.is_idle]
                
                for player in idle_players:
                    task = asyncio.create_task(player.run())
                    player_tasks.append(task)  
                
                prev_context = current_context
            else:
                await asyncio.sleep(5)
        
        if player_tasks:
            await asyncio.gather(*player_tasks)
        
        print(f"[GAME] Round {round_details['Round Number']} completed")
        self.logger.debug(f"Round {round_details['Round Number']} completed")
    
    async def voting_round(self, round_details: dict):
        print(f"\n[GAME] Starting Voting Round {round_details['Round Number']}")
        self.logger.debug(f"Starting Voting Round {round_details['Round Number']}")
        
        votes = defaultdict(int)
        for player in self.players.values():
            vote = await player.vote(round_details=round_details)
            votes[int(vote)] += 1
        
        max_votes = max(votes.values())
        max_voted_players = [player for player, count in votes.items() if count == max_votes]
        
        print(f"[GAME] Voting results: {dict(votes)}")
        self.logger.debug(f"Voting results: {dict(votes)}")
        
        if len(max_voted_players) > 1:
            print(f"[GAME] Tie detected between players: {max_voted_players}. No one is eliminated this round.")
            self.logger.debug(f"Tie detected between players: {max_voted_players}. No one is eliminated this round.")
            return  
        
        max_vote = max_voted_players[0]
        if max_vote in self.players: 
            del self.players[max_vote]
                
            print(f"[GAME] Player {max_vote} has been eliminated by vote!")
            self.logger.debug(f"Player {max_vote} has been eliminated by vote!")

        await self.context_manager.add_message("Game", f"Player {max_vote} has been eliminated!")
        return max_vote in self.imposters