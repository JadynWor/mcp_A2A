import uvicorn
from a2a.types import AgentSkill, AgentCard, AgentCapabilities
import click
from a2a.server.request_handlers import DefaultRequestHandler
import asyncio
from agents.website_builder_simple.agent_executor import WebsiteBuilderSimpleAgentExecutor
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.apps import A2AStarletteApplication

@click.command()
@click.option('--host', default='localhost', help='Host for the agent server')
@click.option('--port', default=10000, help='Port for the agent server')
def main(host:str, port:int):
  """
  Main func to create and run the website builder agent
  """

  skill = AgentSkill(
    id="website_builder_simple_skill",
    name="website_builder_simple_skill",
    description="A simple website builder agent that can create basic web pages",
    tags=["website", "builder", "html", "css", "javascript"],
    examples=[
      """Create a simple webpage with a header and a footer.""",
      """Create a landing page for a product with a call to action button."""
    ]
  )

  agent_card = AgentCard(
    name="website_builder_simple",
    description="A simple website builder agent that can create basic web pages and is built using google's agent development",
    url=f"http://{host}:{port}/",
    skills=[skill],
    version="1.0.0",
    defaultInputModes=["text"],
    defaultOutputModes=["text"],
    capabilities = AgentCapabilities(streaming=True)
  )

  executor = WebsiteBuilderSimpleAgentExecutor()
  asyncio.run(executor.create())

  request_handler = DefaultRequestHandler(
    agent_executor=executor,
    task_store = InMemoryTaskStore()
  )

  server = A2AStarletteApplication(
    agent_card = agent_card,
    http_handler = request_handler
  )

  uvicorn.run(server.build(), host=host, port=port)

if __name__ == "__main__":
  main() # uv run python3 -m agents.website_builder_simple