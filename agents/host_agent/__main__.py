import asyncio
import uvicorn
import click

from a2a.types import AgentSkill, AgentCard, AgentCapabilities
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.apps import A2AStarletteApplication

from agents.host_agent.agent_executor import HostAgentExecutor


async def run(host: str, port: int):
    skill = AgentSkill(
        id="host_agent_skill",
        name="host_agent_skill",
        description="Orchestrator that routes tasks to A2A agents and MCP tools",
        tags=["host", "orchestrator"],
        examples=[
            "Create a simple webpage with a header and a footer using other agents/tools."
        ],
    )

    agent_card = AgentCard(
        name="host_agent",
        description="Orchestrator that routes tasks to A2A agents and MCP tools",
        url=f"http://{host}:{port}/",
        skills=[skill],
        version="1.0.0",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        capabilities=AgentCapabilities(streaming=True),
    )

    agent_executor = HostAgentExecutor()
    await agent_executor.create()

    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor,
        task_store=InMemoryTaskStore(),
    )

    app = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )

    config = uvicorn.Config(app.build(), host=host, port=port)
    server = uvicorn.Server(config)
    await server.serve()


@click.command()
@click.option("--host", default="localhost", help="Host for the agent server")
@click.option("--port", default=10001, help="Port for the agent server")
def main(host: str, port: int):
    asyncio.run(run(host, port))


if __name__ == "__main__":
    main()
