import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def call_tool(tool_name: str, arguments: dict):
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[
            "-m",
            "app.mcp_server.server",
        ],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                tool_name,
                arguments=arguments,
            )

            if result.is_error:
                raise RuntimeError(f"MCP tool failed: {result.content}")

            text = result.content[0].text

            return json.loads(text)
