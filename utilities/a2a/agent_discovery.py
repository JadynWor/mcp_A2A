

import json
import os
from typing import List
from a2a.types import (AgentCard)
from a2a.client import A2ACardResolver, A2AClient
import httpx

class AgentDiscovery:
  """
  Disocvers A2A agent by reading a registry file of URLs
  and querying each ones /.well-known/agent.json endpoint to retrieve
  an agentcard

  Attributes:
    registry_file (str): path to the agent registry file
    base_url (List[str]): List of base URls for A2A agents
  """

  def __init__(self, registry_file: str = None):
    """
    Initializes the AgentDiscovery

    Args:
      registry_file (str): path to the agent registry file
        Defaults to 'utilities/a2a/agent_registry.json'
    """

    if registry_file:
      self.registry_file = registry_file
    else:
      self.registry_file = os.path.join(
        os.path.dirname(__file__),
        'agent_registry.json'
      )
      self.base_urls = self._load_registry()
  
  def _load_registry(self) -> List[str]:
    """
    Load and parse the registry JSON file into list of URLS

    Returns:
      List[str]: List of base URLs for A2A agents
    """
    try:
      with open(self.registry_file, 'r') as f:
        data = json.load(f)
      if not isinstance(data,list):
        raise ValueError("registry file must contain a list of URLs.")
      return data
    except FileNotFoundError:
      print(f"Registry file '{self.registry_file}' not found")
      return []
    except (json.JSONDecodeError, ValueError) as e:
      print (f"Error parsing registry file: {e}")
      return []

  async def list_agent_cards(self) -> list[AgentCard]:
    """
    Async fetches agentcards from each 
    base URL in the registry

    Returns:
      list[AgentCard]: list of agentcards retrived from the agents.
    """
    cards: list[AgentCard] = []

    async with httpx.AsyncClient(timeout=300.0) as httpx_client:
      for base_url in self.base_urls:
        resolver = A2ACardResolver(
          base_url=base_url.rstrip('/'),
          httpx_client=httpx_client
        )
        card = await resolver.get_agent_card()

        cards.append(card)
    return cards