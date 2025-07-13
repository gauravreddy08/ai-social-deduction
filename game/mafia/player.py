from agent.Player import Player
from agents import Runner
from pydantic import BaseModel

class SelectPlayer(BaseModel):
    player_id: str

class MafiaPlayer(Player):
    def __init__(self, name: str, role: str, config: dict):
        self.config = config
        
        super().__init__(name, 
                         generator_instructions=config["generator_instructions"].format(name=name, role=role), 
                         scheduler_instructions=config["scheduler_instructions"].format(name=name, role=role), 
                         generator_model_name=config["generator_model_name"], 
                         scheduler_model_name=config["scheduler_model_name"])
    
    async def run(self) -> bool:
        return await super().run()

    async def vote(self, extra_instructions: str = "") -> str:
        context = await self.context_manager.get_context()
        context += self.config["vote_instructions"] + extra_instructions
        
        model = self.generator.clone(output_type=SelectPlayer)
        
        response = await Runner().run(starting_agent=model, input=context)
        response = response.final_output.player_id
        
        await self.context_manager.add_message(self.name, f"Voted for Player {response}")
        
        return response

    async def kill(self, extra_instructions: str = "") -> str:
        context = await self.context_manager.get_context()
        context += self.config["kill_instructions"] + extra_instructions
        
        model = self.generator.clone(output_type=SelectPlayer)
        
        response = await Runner().run(starting_agent=model, input=context)
        response = response.final_output.player_id
        
        return response