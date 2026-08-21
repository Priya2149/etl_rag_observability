from agent_service.app.services.application_tools import (
    ToolServices,
    build_application_tool_registry,
)
from shared.tools import ToolCall


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


def fake_registry():
    services = ToolServices(
        list_etl_runs=lambda: [{"id": 9}],
        get_etl_run=run_detail,
        search_documents=lambda query: {
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
        },
    )
    return build_application_tool_registry(services)


def test_search_documents_reuses_retrieval_service_result():
    result = fake_registry().execute(
        ToolCall(
            call_id="search-1",
            name="search_documents",
            arguments={"query": "CPU embeddings"},
        )
    )

    assert result.success is True
    assert result.sources == ["guide.txt"]
    assert result.data["evaluation"]["risk_level"] == "low"


def test_latest_dataset_profile_resolves_latest_etl_run():
    result = fake_registry().execute(
        ToolCall(
            call_id="profile-1",
            name="get_dataset_profile",
            arguments={"run_id": None},
        )
    )

    assert result.success is True
    assert result.data["run_id"] == 9
    assert result.data["quality_score"] == 82
    assert "anomaly" in result.data["summary"]


def test_dataset_schema_comes_from_existing_profile():
    result = fake_registry().execute(
        ToolCall(
            call_id="schema-1",
            name="get_dataset_schema",
            arguments={"run_id": 9},
        )
    )

    assert result.success is True
    assert [column["column_name"] for column in result.data["columns"]] == [
        "id",
        "email",
    ]


def test_pipeline_status_is_a_bounded_metadata_lookup():
    result = fake_registry().execute(
        ToolCall(
            call_id="status-1",
            name="get_pipeline_status",
            arguments={"run_id": 9},
        )
    )

    assert result.success is True
    assert result.data["status"] == "completed"
    assert "profile" not in result.data
