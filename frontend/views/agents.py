from __future__ import annotations

import streamlit as st

from api.client import (
    approve_agent_workflow,
    create_agent_workflow,
    get_agent_workflow,
    list_agent_workflows,
    reject_agent_workflow,
    retry_agent_workflow,
)
from components.metrics import metric_card
from components.tables import render_table


def render_step_timeline(steps: list[dict]) -> None:
    if not steps:
        st.info("No workflow steps available.")
        return

    for step in steps:
        status = step.get("status", "unknown")
        icon = "✅" if status == "completed" else "❌" if status == "failed" else "⏳"

        with st.expander(
            f"{icon} {step.get('agent_name')} → {step.get('step_name')} ({status})",
            expanded=True,
        ):
            col1, col2 = st.columns(2)

            with col1:
                st.caption("Input")
                st.json(step.get("input_payload"))

            with col2:
                st.caption("Output")
                st.json(step.get("output_payload"))

            st.caption(f"Duration: {step.get('duration_ms')} ms")

            if step.get("error_message"):
                st.error(step.get("error_message"))


def render_agent_workflows() -> None:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Agentic Workflow Orchestrator</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Run and inspect traceable multi-agent workflows with human approval checkpoints.</div>',
        unsafe_allow_html=True,
    )

    question = st.text_area(
        "Workflow Question",
        placeholder="Example: Analyze the latest dataset quality and retrieve related documentation.",
        height=100,
    )

    dataset_id = st.number_input("ETL Run ID / Dataset ID (optional)", min_value=0, step=1)

    if st.button("Start Agent Workflow"):
        try:
            result = create_agent_workflow(
                dataset_id=int(dataset_id) if dataset_id else None,
                question=question if question.strip() else None,
            )
            st.session_state["last_workflow_id"] = result["workflow_id"]
            st.success("Workflow started.")
            st.json(result)
        except Exception as e:
            st.error(f"Failed to start workflow: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Recent Workflows</div>', unsafe_allow_html=True)

    try:
        workflows = list_agent_workflows()
        render_table(workflows)
    except Exception as e:
        st.error(f"Failed to load workflows: {e}")
        workflows = []

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Workflow Trace</div>', unsafe_allow_html=True)

    default_id = st.session_state.get("last_workflow_id", 1)
    workflow_id = st.number_input("Workflow ID", min_value=1, step=1, value=int(default_id))

    if st.button("Load Workflow Trace"):
        try:
            workflow = get_agent_workflow(int(workflow_id))

            row = st.columns(4)
            with row[0]:
                metric_card("Workflow ID", workflow.get("id"), "Run identifier")
            with row[1]:
                metric_card("Status", workflow.get("status"), "Workflow state")
            with row[2]:
                metric_card("Current Step", workflow.get("current_step"), "Active checkpoint")
            with row[3]:
                metric_card("Name", workflow.get("workflow_name"), "Workflow type")

            st.markdown("### Step Timeline")
            render_step_timeline(workflow.get("steps", []))

            st.markdown("### Final Output")
            if workflow.get("final_output"):
                st.json(workflow.get("final_output"))
            else:
                st.info("Final output is not available yet.")

            if workflow.get("status") == "waiting_for_approval":
                col1, col2 = st.columns(2)

                with col1:
                    if st.button("Approve Workflow"):
                        result = approve_agent_workflow(int(workflow_id))
                        st.success("Workflow approved.")
                        st.json(result)

                with col2:
                    if st.button("Reject Workflow"):
                        result = reject_agent_workflow(int(workflow_id))
                        st.warning("Workflow rejected.")
                        st.json(result)

            if workflow.get("status") == "failed":
                if st.button("Retry Failed Workflow"):
                    result = retry_agent_workflow(int(workflow_id))
                    st.success("Workflow retried.")
                    st.json(result)

        except Exception as e:
            st.error(f"Failed to load workflow: {e}")

    st.markdown("</div>", unsafe_allow_html=True)