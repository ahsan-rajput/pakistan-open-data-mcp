import asyncio
from mcp import Client

async def main():
    async with Client("https://pakistan-open-data-mcp.onrender.com/mcp") as client:
        tools = await client.list_tools()
        print("Connected! Available tools:")
        for tool in tools.tools:
            print(" -", tool.name)

asyncio.run(main())