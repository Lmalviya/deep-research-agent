import asyncio
import json
import os
from typing import Dict, List, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

load_dotenv()

class SmartMCPClient:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.sessions: Dict[str, ClientSession] = {}
        self.exit_stack = asyncio.ExitStack()

    async def load_config(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        with open(self.config_path, "r") as f:
            return json.load(f)

    async def connect_to_server(self, server_name: str, server_config: Dict[str, Any]):
        print(f"🔌 Connecting to server: {server_name}...")
        
        # Extract command and args
        command = server_config.get("command")
        args = server_config.get("args", [])
        env = {**os.environ, **server_config.get("env", {})}

        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=env
        )

        # Create a persistent connection
        # We use the exit_stack to manage the context managers
        transport_ctx = stdio_client(server_params)
        read, write = await self.exit_stack.enter_async_context(transport_ctx)
        session = await self.exit_stack.enter_async_context(ClientSession(read, write))
        
        # Initialize the session
        await session.initialize()
        self.sessions[server_name] = session
        print(f"✅ Connected to {server_name}")

    async def list_all_tools(self):
        all_tools = {}
        for name, session in self.sessions.items():
            tools = await session.list_tools()
            all_tools[name] = tools.tools
        return all_tools

    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]):
        if server_name not in self.sessions:
            return f"Error: Server {server_name} not found."
        
        session = self.sessions[server_name]
        try:
            result = await session.call_tool(tool_name, arguments)
            return result.content
        except Exception as e:
            return f"Error calling tool {tool_name} on {server_name}: {str(e)}"

    async def run(self):
        config = await self.load_config()
        servers = config.get("mcpServers", {})

        # Connect to all servers in parallel
        tasks = [self.connect_to_server(name, cfg) for name, cfg in servers.items()]
        await asyncio.gather(*tasks)

        print("\n--- Available Tools ---")
        tools_map = await self.list_all_tools()
        for server, tools in tools_map.items():
            print(f"\n[{server}]")
            for tool in tools:
                print(f"  - {tool.name}: {tool.description}")

        print("\n--- Testing Retrieval ---")
        # Example call to the retrieval-hub
        if "retrieval-hub" in self.sessions:
            print("\nCalling internet_search on retrieval-hub...")
            result = await self.call_tool(
                "retrieval-hub", 
                "internet_search", 
                {"query": "Latest news on MCP protocol", "search_depth": "basic"}
            )
            print(f"Result: {result}")

    async def cleanup(self):
        await self.exit_stack.aclose()

async def main():
    config_path = "packages/mcp-smart-client/mcp_config.json"
    client = SmartMCPClient(config_path)
    try:
        await client.run()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
