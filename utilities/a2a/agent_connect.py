from uuid import uuid4
from typing import Any

import httpx
from a2a.client import A2AClient
from a2a.types import AgentCard

# These names vary by SDK version. If your version differs, we’ll adjust after the next error.
from a2a.types import SendMessageRequest, MessageSendParams  # keep if they exist


class AgentConnector:
  """
  Connects to a remote A2A Agent and provides uniform method to delegate tasks
  """

  def __init__(self, agent_card: AgentCard):
    self.agent_card = agent_card

  async def send_task(self, message: str, session_id: str) -> str:
    """
    Send a user message to the agent and return the agent's text response.
    """

    async with httpx.AsyncClient(timeout=300.0) as httpx_client:
      a2a_client = A2AClient(
        httpx_client=httpx_client,
        agent_card=self.agent_card,
      )

      send_message_payload: dict[str, Any] = {
        "message": {
          "role": "user",
          "messageId": str(uuid4()),
          "parts": [{"text": message, "kind": "text"}],
        }
      }

      # Build request using the SDK models
      request = SendMessageRequest(
        id=str(uuid4()),
        params=MessageSendParams(**send_message_payload),
      )

      response = await a2a_client.send_message(request=request)
      response_data = response.model_dump(mode="json", exclude_none=True)

      try:
        return response_data["result"]["status"]["message"]["parts"][0]["text"]
      except (KeyError, IndexError, TypeError):
        return "No response from agent."
