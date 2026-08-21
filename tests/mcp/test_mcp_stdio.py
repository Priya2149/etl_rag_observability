import asyncio
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


def run_async(coroutine):
    # Keep this protocol loop independent from Playwright's synchronous loop.
    with ThreadPoolExecutor(max_workers=1) as executor:
        return executor.submit(asyncio.run, coroutine).result()


def test_stdio_server_launches_and_supports_discovery():
    async def exercise(parameters):
        async with (
            stdio_client(parameters) as (read_stream, write_stream),
            ClientSession(read_stream, write_stream) as session,
        ):
            initialized = await session.initialize()
            result = await session.list_tools()
        return initialized, result

    repository_root = Path(__file__).resolve().parents[2]
    parameters = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_service.server"],
        cwd=repository_root,
        env=os.environ.copy(),
    )

    initialized, result = run_async(exercise(parameters))

    assert initialized.server_info.name == "etl-rag-observability"
    assert {tool.name for tool in result.tools} == {
        "search_documents",
        "get_dataset_schema",
        "get_dataset_profile",
        "get_pipeline_status",
    }
