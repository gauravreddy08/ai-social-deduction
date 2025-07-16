from agent.Player import Player
from agents import Runner
from pydantic import BaseModel
import json
from game.undercover.prompts import CONTRIBUTE_WORD_PROMPT, VOTING_PROMPT

class SelectPlayer(BaseModel):
    player_id: str

class SayWord(BaseModel):
    word: str

class UndercoverPlayer(Player):
    def __init__(self, player_details: dict, config: dict):
        self.config = config
        self.player_details = json.dumps(player_details)
        
        super().__init__(name=player_details["name"], 
                         generator_instructions=config["generator_instructions"].format(player_details=self.player_details), 
                         scheduler_instructions=config["scheduler_instructions"].format(player_details=self.player_details), 
                         generator_model_name=config["generator_model_name"], 
                         scheduler_model_name=config["scheduler_model_name"])
    
    
    
    async def run(self) -> bool:
        return await super().run()

    async def vote(self, round_details: dict) -> str:
        
        context = await self.context_manager.get_context()
        round_details = json.dumps(round_details)
        context += self.config["voting_instructions"].format(round_details=round_details)
        
        model = self.generator.clone(output_type=SelectPlayer)
        
        response = await Runner().run(starting_agent=model, input=context)
        response = response.final_output.player_id
        
        await self.context_manager.add_message(self.name, f"Voted for Player {response}")
        
        return response

    async def contribute_word(self, round_details: dict) -> str:
        context = await self.context_manager.get_context()
        round_details = json.dumps(round_details)
        context += self.config["contribute_word_instructions"].format(round_details=round_details)
        
        model = self.generator.clone(output_type=SayWord)
            
        response = await Runner().run(starting_agent=model, input=context)
        response = response.final_output.word

        await self.context_manager.add_message(self.name, f"Said word: {response}")
        
        return response