from google.adk.models.google_llm import Gemini
from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a

from generate_tool import proxy_generate

from dotenv import load_dotenv

load_dotenv()

# a simple agent which will be wrapped by a2a to act as a2a agent
_generate_song = Agent(
    name="generate_song_agent",
    model=Gemini(model="gemini-2.5-flash-lite"), 
    description="An A2A Agent that can take queries of generating songs.",
    instruction="""
    You are an A2A Agent that can generate audio using tool 'proxy_generate'.
    - You will be given a JSON string
    - You must return serializable JSON String
    """,
    tools=[proxy_generate],
)

generate_song_a2a = to_a2a(_generate_song, port=7860) # we made the LLM agent an A2AServer
# Checking the server

# uvicorn agent:generate_song_a2a --host 0.0.0.0 --port 8000 --reload