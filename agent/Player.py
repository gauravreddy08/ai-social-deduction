from agents import Runner
from agent.generator import get_generator_agent
from agent.scheduler import get_scheduler_agent
from context.Context import Context
from datetime import datetime
import asyncio
import dotenv

dotenv.load_dotenv(override=True)

class Player:
    def __init__(self, name: str, generator_instructions: str, scheduler_instructions: str, generator_model_name: str, scheduler_model_name: str):
        self.name = name
        self.is_idle = True
        
        self.generator = get_generator_agent(name, 
                                             instructions=generator_instructions, 
                                             model_name=generator_model_name)
        
        self.scheduler = get_scheduler_agent(name, 
                                             instructions=scheduler_instructions, 
                                             model_name=scheduler_model_name)
        
        self.context_manager = Context()
    
    async def run(self) -> bool:
        context = await self.context_manager.get_context()

        response = await Runner().run(starting_agent=self.scheduler, input=context)
        response = response.final_output
        
        if response.should_speak == "false": return False
        self.is_idle = False
        await self.context_manager.add_typing(self.name)

        start_time = datetime.now()
        response = await Runner().run(starting_agent=self.generator, input=context)
        response = response.final_output
        delay = (40 * len(response.split(" "))) / 60

        await asyncio.sleep(delay - (datetime.now() - start_time).total_seconds())
        await self.context_manager.add_message(self.name, response)
        self.is_idle = True
        return True

    