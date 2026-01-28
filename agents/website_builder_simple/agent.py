from collections.abc import AsyncIterable
from utilities.common.file_loader import load_instruction_file
from google.adk.agents import LlmAgent
from google.adk import Runner

from google.adk.artifacts import InMemoryArtifactService
from google.adk.sessions import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService

from google.genai import types

from dotenv import load_dotenv
load_dotenv()

class WebsiteBuilderSimple:
  """
  A simple website builder agent that can create basic web pages 
  and is built using google's agent development framework.
  """

  def __init__(self):
    self.system_instruction = load_instruction_file("agents/website_builder_simple/instructions.txt")
    self.description = load_instruction_file("agents/website_builder_simple/description.txt")

    self._agent = None
    self._runner = None
    self._user_id = "website_builder_user"

  async def create(self):
    self._agent = self._build_agent()
    self._runner = Runner(
      app_name=self._agent.name,
      agent=self._agent,
      artifact_service=InMemoryArtifactService(),
      session_service=InMemorySessionService(),
      memory_service=InMemoryMemoryService(),
  )

  def _build_agent(self) -> LlmAgent:
    return LlmAgent(
      name="website_builder_simple",
      model="gemini-flash-latest",
      instruction=self.system_instruction,
      description=self.description
    )
  
  async def invoke(self, query:str, session_id: str) -> AsyncIterable[dict]:
    """
    Invoke Agent
    Return stream of updates back to caller
    """

    session = await self._runner.session_service.get_session(
      app_name = self._agent.name,
      session_id = session_id,
      user_id = self._user_id,
    )

    if not session:
      session = await self._runner.session_service.create_session(
      app_name = self._agent.name,
      session_id = session_id,
      user_id = self._user_id,
    )
      
    user_content = types.Content(
      role="user",
      parts=[types.Part.from_text(text=query)]
    )

    async for event in self._runner.run_async(
      user_id = self._user_id,
      session_id = session_id,
      new_message = user_content
    ):
      if event.is_final_response():
        final_response = ""
        if event.content and event.content.parts and event.content.parts[-1].text:
          final_response = event.content.parts[-1].text

        yield {
          'is_task_complete': True,
          'content': final_response
        }
      else:
        yield{
          'is_task_complete': False,
          'updates': 'Agent is processing your request...'
        }