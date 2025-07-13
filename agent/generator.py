from agents import Agent
from pydantic import BaseModel

def get_generator_agent(name: str, instructions: str, model_name: str, output_type: BaseModel | None = None):
    return Agent(
        name=name,
        instructions=instructions,
        model=model_name,
        output_type=output_type,
    )