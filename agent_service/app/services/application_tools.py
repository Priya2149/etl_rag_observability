from dataclasses import dataclass
from typing import Any

from shared.tools import (
    ApplicationTool,
    DatasetProfileInput,
    DatasetProfileOutput,
    DatasetSchemaInput,
    DatasetSchemaOutput,
    PipelineStatusInput,
    PipelineStatusOutput,
    SearchDocumentsInput,
    SearchDocumentsOutput,
    ToolExecutionError,
    ToolRegistry,
)

from .tool_client import (
    ServiceToolError,
    get_etl_run_details,
    get_etl_runs,
    search_rag_documents,
)


@dataclass(frozen=True)
class ToolServices:
    list_etl_runs: Any = get_etl_runs
    get_etl_run: Any = get_etl_run_details
    search_documents: Any = search_rag_documents


def _get_run(run_id: int | None, services: ToolServices) -> dict:
    try:
        if run_id is not None:
            return services.get_etl_run(run_id)

        runs = services.list_etl_runs()
        if not runs:
            raise ToolExecutionError("No ETL pipeline runs are available.")
        return services.get_etl_run(runs[0]["id"])
    except ServiceToolError as exc:
        raise ToolExecutionError(str(exc)) from exc


def build_application_tool_registry(
    services: ToolServices | None = None,
) -> ToolRegistry:
    services = services or ToolServices()

    def search_documents(payload: SearchDocumentsInput) -> SearchDocumentsOutput:
        try:
            result = services.search_documents(payload.query)
        except ServiceToolError as exc:
            raise ToolExecutionError(str(exc)) from exc

        sources = result.get("source_files", [])
        chunks = result.get("retrieved_chunks", [])
        summary = (
            f"Found {len(chunks)} relevant document chunks from "
            f"{len(sources)} source files."
            if chunks
            else "No relevant document chunks were found."
        )
        return SearchDocumentsOutput(
            query=payload.query,
            retrieved_chunks=chunks,
            sources=sources,
            evaluation={
                "best_distance": result.get("best_distance"),
                "risk_level": result.get("risk_level"),
                "evaluation_status": result.get("evaluation_status"),
                "warning_flags": result.get("warning_flags", []),
            },
            summary=summary,
        )

    def get_dataset_schema(payload: DatasetSchemaInput) -> DatasetSchemaOutput:
        run = _get_run(payload.run_id, services)
        profile = run.get("profile") or {}
        columns = profile.get("columns", [])
        issues = profile.get("schema_issues", [])
        return DatasetSchemaOutput(
            run_id=run["id"],
            filename=run["filename"],
            columns=columns,
            schema_issues=issues,
            summary=(
                f"Dataset {run['filename']} has {len(columns)} profiled columns "
                f"and {len(issues)} schema issues."
            ),
        )

    def get_dataset_profile(payload: DatasetProfileInput) -> DatasetProfileOutput:
        run = _get_run(payload.run_id, services)
        anomalies = run.get("anomalies")
        anomaly_count = len(anomalies) if hasattr(anomalies, "__len__") else 0
        return DatasetProfileOutput(
            run_id=run["id"],
            filename=run["filename"],
            status=run["status"],
            quality_score=run.get("quality_score"),
            total_rows=run.get("total_rows"),
            total_columns=run.get("total_columns"),
            anomalies=anomalies,
            profile=run.get("profile"),
            summary=(
                f"ETL run {run['id']} for {run['filename']} has status "
                f"{run['status']}, quality score {run.get('quality_score')}, "
                f"and {anomaly_count} detected anomaly groups."
            ),
        )

    def get_pipeline_status(payload: PipelineStatusInput) -> PipelineStatusOutput:
        run = _get_run(payload.run_id, services)
        error_detail = (
            f" Error: {run['error_message']}" if run.get("error_message") else ""
        )
        return PipelineStatusOutput(
            run_id=run["id"],
            filename=run["filename"],
            status=run["status"],
            quality_score=run.get("quality_score"),
            processing_time_ms=run.get("processing_time_ms"),
            error_message=run.get("error_message"),
            summary=(
                f"ETL run {run['id']} for {run['filename']} is {run['status']}."
                f"{error_detail}"
            ),
        )

    return ToolRegistry(
        [
            ApplicationTool(
                name="search_documents",
                description=(
                    "Search the indexed documents using semantic retrieval and return "
                    "grounded chunks, sources, and retrieval quality metadata."
                ),
                input_model=SearchDocumentsInput,
                output_model=SearchDocumentsOutput,
                handler=search_documents,
            ),
            ApplicationTool(
                name="get_dataset_schema",
                description=(
                    "Get the profiled columns and schema issues for an ETL run. "
                    "Use null run_id for the latest run."
                ),
                input_model=DatasetSchemaInput,
                output_model=DatasetSchemaOutput,
                handler=get_dataset_schema,
            ),
            ApplicationTool(
                name="get_dataset_profile",
                description=(
                    "Get quality score, dimensions, anomalies, and statistical profile "
                    "for an ETL run. Use null run_id for the latest run."
                ),
                input_model=DatasetProfileInput,
                output_model=DatasetProfileOutput,
                handler=get_dataset_profile,
            ),
            ApplicationTool(
                name="get_pipeline_status",
                description=(
                    "Get status, processing time, and safe error details for an ETL "
                    "pipeline run. Use null run_id for the latest run."
                ),
                input_model=PipelineStatusInput,
                output_model=PipelineStatusOutput,
                handler=get_pipeline_status,
            ),
        ]
    )
