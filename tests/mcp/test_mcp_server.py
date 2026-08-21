import asyncio
from concurrent.futures import ThreadPoolExecutor

from mcp import Client

from agent_service.app.services.application_tools import (
    ToolServices,
    build_application_tool_registry,
)
from mcp_service.server import create_mcp_server


def run_async(coroutine):
    # Playwright's synchronous plugin can retain an event loop between test modules.
    with ThreadPoolExecutor(max_workers=1) as executor:
        return executor.submit(asyncio.run, coroutine).result()


def run_detail(run_id=9):
    return {
        "id": run_id,
        "filename": "customers.csv",
        "status": "completed",
        "quality_score": 82,
        "total_rows": 100,
        "total_columns": 2,
        "processing_time_ms": 25,
        "error_message": None,
        "anomalies": {"missing_values": ["email"]},
        "profile": {
            "columns": [
                {"column_name": "id", "inferred_type": "integer"},
                {"column_name": "email", "inferred_type": "string"},
            ],
            "schema_issues": ["email has missing values"],
        },
    }


def fake_registry(*, list_runs=None, get_run=None, search=None):
    services = ToolServices(
        list_etl_runs=list_runs or (lambda: [{"id": 9}]),
        get_etl_run=get_run or run_detail,
        search_documents=search
        or (
            lambda query: {
                "retrieved_chunks": [
                    {
                        "content": f"Evidence for {query}",
                        "metadata": {"source": "guide.txt"},
                    }
                ],
                "source_files": ["guide.txt"],
                "best_distance": 0.2,
                "risk_level": "low",
                "evaluation_status": "good",
                "warning_flags": [],
            }
        ),
    )
    return build_application_tool_registry(services)


def test_server_initializes_and_discovers_shared_tool_schemas():
    async def exercise(registry):
        async with Client(create_mcp_server(registry)) as client:
            return await client.list_tools()

    registry = fake_registry()
    result = run_async(exercise(registry))

    tools = {tool.name: tool for tool in result.tools}
    assert set(tools) == {
        "search_documents",
        "get_dataset_schema",
        "get_dataset_profile",
        "get_pipeline_status",
    }
    assert tools["search_documents"].input_schema["properties"]["query"][
        "type"
    ] == "string"
    assert tools["get_pipeline_status"].annotations.read_only_hint is True
    assert tools["get_pipeline_status"].annotations.destructive_hint is False
    assert tools["search_documents"].description == registry.definitions()[0][
        "description"
    ]


def test_mcp_invocation_reuses_shared_registry(monkeypatch):
    async def exercise(registry):
        async with Client(create_mcp_server(registry)) as client:
            return await client.call_tool(
                "search_documents", {"query": "CPU embeddings"}
            )

    registry = fake_registry()
    calls = []
    execute = registry.execute

    def record_call(call):
        calls.append(call)
        return execute(call)

    monkeypatch.setattr(registry, "execute", record_call)
    result = run_async(exercise(registry))

    assert result.is_error is False
    assert result.structured_content["success"] is True
    assert result.structured_content["data"]["sources"] == ["guide.txt"]
    assert calls[0].name == "search_documents"
    assert calls[0].arguments == {"query": "CPU embeddings"}


def test_mcp_etl_tool_returns_structured_status():
    async def exercise():
        async with Client(create_mcp_server(fake_registry())) as client:
            return await client.call_tool("get_pipeline_status", {"run_id": 9})

    result = run_async(exercise())

    assert result.is_error is False
    assert result.structured_content["success"] is True
    assert result.structured_content["data"]["run_id"] == 9
    assert result.structured_content["data"]["status"] == "completed"


def test_shared_validation_returns_a_safe_structured_failure():
    async def exercise():
        async with Client(create_mcp_server(fake_registry())) as client:
            return await client.call_tool("get_pipeline_status", {"run_id": 0})

    result = run_async(exercise())

    assert result.is_error is False
    assert result.structured_content["success"] is False
    assert result.structured_content["error"] == (
        "Invalid arguments for tool 'get_pipeline_status'."
    )


def test_missing_resource_returns_a_safe_structured_failure():
    async def exercise(registry):
        async with Client(create_mcp_server(registry)) as client:
            return await client.call_tool(
                "get_dataset_profile", {"run_id": None}
            )

    registry = fake_registry(list_runs=list)
    result = run_async(exercise(registry))

    assert result.is_error is False
    assert result.structured_content["success"] is False
    assert result.structured_content["error"] == (
        "No ETL pipeline runs are available."
    )


def test_unexpected_tool_errors_are_sanitized():
    async def exercise(registry):
        async with Client(create_mcp_server(registry)) as client:
            return await client.call_tool("search_documents", {"query": "safe"})

    def fail(_query):
        raise ValueError("database password appeared here")

    registry = fake_registry(search=fail)
    result = run_async(exercise(registry))

    payload = result.structured_content
    assert payload["success"] is False
    assert payload["error"] == "Tool 'search_documents' failed."
    assert "password" not in str(payload)
