from collections.abc import AsyncIterable
from uuid import uuid4
from utilities.a2a.agent_connect import AgentConnector
from utilities.a2a.agent_discovery import AgentDiscovery
from utilities.common.file_loader import load_instruction_file
from rich import print as rprint
from rich.syntax import Syntax
from typing import Any
from google.adk.agents import LlmAgent
from google.adk import Runner
from google.adk.tools.function_tool import FunctionTool
from google.adk.artifacts import InMemoryArtifactService
from google.adk.sessions import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
#from utilities.rules.rule_engine import RuleEngine

import json
from google.genai import types
from utilities.mcp.mcp_connector import MCPConnector
from a2a.types import AgentCard

from dotenv import load_dotenv
load_dotenv()

class HostAgent:
  """
  Orchastrator agent
  - Discover a2a agents via agent disocvery
  - Disovers the mcp server via mcp connection and load mcp tools 
  - Routes the user query by picking the correct agent/tool
  """

  def __init__(self):
    self.system_instruction = load_instruction_file("agents/host_agent/instructions.txt")
    self.description = load_instruction_file("agents/host_agent/description.txt")

    self.MCPConnector = MCPConnector()
    self.AgentDiscovery = AgentDiscovery()

    self._agent = None
    self._user_id = "host_agent_user"
    self._runner = None
    #self.rule_engine = RuleEngine() #continue from here to build rule engine

  async def create(self):
    self._agent = await self._build_agent()
    self._runner = Runner(
      app_name = self._agent.name,
      agent = self._agent,
      artifact_service = InMemoryArtifactService(),
      session_service = InMemorySessionService(),
      memory_service = InMemoryMemoryService(),
    )
  
  async def _list_agents(self)-> list[dict]:
    """
    A2A tool: returns the list of dict agent card objects of registered child agents
    Returns:
      list[AgentCard]: list of agent card objects
    """
    cards = await self.AgentDiscovery.list_agent_cards()

    return [card.model_dump(exclude_none=True) for card in cards]
  
  async def _delegate_task(self, agent_name:str, message:str) -> str:
    matched_card = None
    cards = await self.AgentDiscovery.list_agent_cards()

    for card in cards:
      if card.name.lower() == agent_name.lower() or getattr(card, "id", "").lower() == agent_name.lower():
        matched_card = card
        break    
    if matched_card is None:
      return "Agent not found"
    
    connector = AgentConnector(agent_card=matched_card)
    return await connector.send_task(message=message, session_id=str(uuid4()))
    
  async def _build_agent(self) -> LlmAgent:

    mcp_tools = await self.MCPConnector.get_tools()

    return LlmAgent(
      name="host_agent",
      model="gemini-flash-latest",
      instruction=self.system_instruction,
      description=self.description,
      tools=[
        FunctionTool(self._delegate_task),
        FunctionTool(self._list_agents),
        *mcp_tools
      ]
    )
  
  #implement helper function so rule engine can be fed into when invoked

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
      print_json_response = (event, "====================================== NEW EVENT ======================================")

      print (f"is_final_response: {event.is_final_response()}")

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

def print_json_response(response: Any, title: str ) -> None:
  #Display a formatted color highlighted view of response object
  print(f"\n==={title}===\n")
  try:
    if hasattr(response, "root"): #check if response is wrapped by sdk
      data = response.root.model_dump(mode="json", exclude_none=True)
    else:
      data = response.model_dump(mode="json", exclude_none=True)

    json_str = json.dumps(data, indent=2, ensure_ascii=False) #convert dict to pretty JSON string
    syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
    rprint(syntax)
  except Exception as e:
    rprint(f"[red]Error displaying response:[/red] {e}")
    rprint(repr(response))