import asyncio
from utilities.mcp.mcp_discovery import MCPDiscovery
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
from mcp import StdioServerParameters

class MCPConnector:
  """
  Discovers the MCP servers from the config, loads each server's tools,
  and caches them as MCPToolsets compatible with Google's ADK.
  """

  def __init__(self, config_file: str = None):
    self.discovery = MCPDiscovery(config_file=config_file)
    self.tools: list[MCPToolset] = []

  async def _load_all_tools(self):
    tools = []

    for name, server in self.discovery.list_servers().items():
      try:
        if server.get("command") == "streamable_http":
          conn = StreamableHTTPServerParams(url=server["args"][0])
        else:
          conn = StdioConnectionParams(
            server_params=StdioServerParameters(
              command=server["command"],
              args=server["args"],
            ),
            timeout=5,
          )

        tool_list = await asyncio.wait_for(
          MCPToolset(connection_params=conn).get_tools(),
          timeout=15.0,
        )

        if tool_list:
          mcp_toolset = MCPToolset(connection_params=conn)
          tool_names = [tool.name for tool in tool_list]
          print(f"Loaded tools from server '{name}': {', '.join(tool_names)}")
          tools.append(mcp_toolset)

      except asyncio.TimeoutError as e:
        print(f"Timeout while loading tools from server '{name}': {e}")
      except ConnectionError as e:
        print(f"Connection error while loading tools from server '{name}': {e}")
      except Exception as e:
        print(f"Error while loading tools from server '{name}': {e}")

    self.tools = tools
    return tools

  async def get_tools(self) -> list[MCPToolset]:
    """
    Loads and returns the cached list of MCPToolsets.
    """
    if not self.tools:
      await self._load_all_tools()
    return self.tools
