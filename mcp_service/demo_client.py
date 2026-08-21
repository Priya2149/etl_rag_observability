import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


async def run_demo(
    run_id: int | None,
    etl_base_url: str,
    rag_base_url: str,
) -> dict:
    repository_root = Path(__file__).resolve().parents[1]
    server_environment = os.environ.copy()
    server_environment["ETL_BASE_URL"] = etl_base_url
    server_environment["RAG_BASE_URL"] = rag_base_url
    parameters = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_service.server"],
        cwd=repository_root,
        env=server_environment,
    )
    async with (
        stdio_client(parameters) as (read_stream, write_stream),
        ClientSession(read_stream, write_stream) as session,
    ):
        await session.initialize()
        tools = await session.list_tools()
        result = await session.call_tool("get_pipeline_status", {"run_id": run_id})
        return {
            "tools": [tool.name for tool in tools.tools],
            "invocation": result.structured_content,
            "is_error": result.is_error,
        }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Discover MCP tools and invoke the ETL pipeline-status tool."
    )
    parser.add_argument(
        "--run-id",
        type=int,
        default=None,
        help="ETL run ID; omit to use the latest run.",
    )
    parser.add_argument(
        "--etl-base-url",
        default="http://localhost:8000",
        help="ETL service URL available to the MCP server process.",
    )
    parser.add_argument(
        "--rag-base-url",
        default="http://localhost:8001",
        help="RAG service URL available to the MCP server process.",
    )
    arguments = parser.parse_args()
    result = asyncio.run(
        run_demo(
            arguments.run_id,
            arguments.etl_base_url,
            arguments.rag_base_url,
        )
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
