import asyncio
from agents import Agent, Runner
from pydantic import BaseModel

class ShouldSpeak(BaseModel):
    should_speak: bool

def get_scheduler_agent(name: str, instructions: str, model_name: str, output_type: BaseModel | None = ShouldSpeak):
    return Agent(
        name=name,
        instructions=instructions,
        model=model_name,
        output_type=ShouldSpeak,
    )