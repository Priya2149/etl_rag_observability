def test_streamlit_homepage_loads(page):
    page.goto("http://localhost:8501")

    page.get_by_text("Data + AI Reliability Platform").wait_for(timeout=10000)

    assert page.get_by_text("Overview").is_visible()
    assert page.get_by_text("ETL").is_visible()
    assert page.get_by_text("RAG").is_visible()
    assert page.get_by_text("Failures").is_visible()


def test_rag_page_navigation(page):
    page.goto("http://localhost:8501")

    page.get_by_text("RAG").click()

    page.get_by_text("Upload Text Document").wait_for(timeout=10000)
    page.get_by_text("Ask a Question").wait_for(timeout=10000)


def test_etl_page_navigation(page):
    page.goto("http://localhost:8501")

    page.get_by_text("ETL").click()

    page.get_by_text("Upload CSV").wait_for(timeout=10000)
    page.get_by_text("ETL Runs").wait_for(timeout=10000)


def test_agents_page_navigation(page):
    page.goto("http://localhost:8501")

    page.get_by_text("Agents").click()

    page.get_by_text("Agentic Workflow Orchestrator").wait_for(timeout=10000)