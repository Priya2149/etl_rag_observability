from uuid import uuid4

from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from agent_service.app.services.application_tools import (
    build_application_tool_registry,
)
from shared.tools import ToolCall, ToolExecutionResult, ToolRegistry

SERVER_INSTRUCTIONS = """Read-only access to bounded ETL metadata and indexed-document
retrieval. Tool inputs are validated and failures are returned as sanitized structured
results. This server never provides SQL, shell execution, arbitrary filesystem access,
or secrets. Use run_id=null when the user asks for the latest ETL run."""

READ_ONLY_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=True,
)


def create_mcp_server(registry: ToolRegistry | None = None) -> MCPServer:
    registry = registry or build_application_tool_registry()
    descriptions = {
        definition["name"]: definition["description"]
        for definition in registry.definitions()
    }
    server = MCPServer(
        name="etl-rag-observability",
        title="ETL/RAG Observability Tools",
        description="Safe read-only access to the repository's ETL and RAG capabilities.",
        instructions=SERVER_INSTRUCTIONS,
        version="1.0.0",
    )

    def invoke(name: str, arguments: dict) -> ToolExecutionResult:
        return registry.execute(
            ToolCall(
                call_id=f"mcp-{uuid4()}",
                name=name,
                arguments=arguments,
            )
        )

    def search_documents(query: str) -> ToolExecutionResult:
        return invoke("search_documents", {"query": query})

    def get_dataset_schema(run_id: int | None = None) -> ToolExecutionResult:
        return invoke("get_dataset_schema", {"run_id": run_id})

    def get_dataset_profile(run_id: int | None = None) -> ToolExecutionResult:
        return invoke("get_dataset_profile", {"run_id": run_id})

    def get_pipeline_status(run_id: int | None = None) -> ToolExecutionResult:
        return invoke("get_pipeline_status", {"run_id": run_id})

    handlers = {
        "search_documents": search_documents,
        "get_dataset_schema": get_dataset_schema,
        "get_dataset_profile": get_dataset_profile,
        "get_pipeline_status": get_pipeline_status,
    }
    for name, handler in handlers.items():
        server.add_tool(
            handler,
            name=name,
            description=descriptions[name],
            annotations=READ_ONLY_ANNOTATIONS,
            structured_output=True,
        )

    return server


mcp = create_mcp_server()


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
