--Simple multi agent setup with a Host Agent that discovers MCP tools and routes requests to agents like a website builder. Includes a streamable HTTP MCP server plus a cli to talk to the Host Agent(orchestrater)

Requirements

Python 3.12+
uv installed

Setup

Install dependencies

uv sync

Create a .env file in the project root

Create a file named .env in the root of the project.

Add your Google API key

Go here to generate an API key
https://aistudio.google.com/api-keys

Add this to your .env file

GOOGLE_API_KEY=ur_key

Run

Open separate terminals for the components you want to run.

streamable-HTTP MCP server -> uv run mcp/servers/streamable_http_server.py

Website builder agent -> uv run python3 -m agents.website_builder_simple

Host agent -> uv run python -m agents.host_agent

CLI -> uv run python -m app.cli.cmd

The CLI will prompt you for input. Type q or quit to exit.

Notes

If you get a port already in use error,
  list all processes: lsof -i :x
  kill process pid: kill -9 <PID>
stop the existing process using that port and rerun the server.
The host agent is responsible for loading MCP tools and orchestrating tasks.


flowchart LR
  U[User] --> FE[App/CLI]
  FE --> A2AC[A2A Client]

  A2AC --> HOST["Host Agent Orchestrator<br/>A2A Server"]

  HOST --> REG["Agent Registry<br/>agent_registry.json"]
  HOST --> CONN["Agent Connector<br/>A2A Client"]

  CONN --> AG1["Website Builder Agent<br/>A2A Server"]
  CONN --> AGN["Other Remote Agent<br/>A2A Server"]

  HOST --> MCPC["MCP Connector<br/>reads mcp_config.json"]
  MCPC --> MCPCLI["MCP Client"]

  MCPCLI --> MCP1["MCP Server<br/>terminal_server"]
  MCPCLI --> MCPN["MCP Server<br/>other tools"]

  MCP1 --> T1["MCP Tools"]
  MCPN --> TN["MCP Tools"]
