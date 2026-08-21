APP_URL = "http://localhost:8501"
APP_TITLE = "Data + AI Reliability Platform"


def open_app(page):
    response = page.goto(APP_URL)

    assert response is not None
    assert response.ok
    page.get_by_text(APP_TITLE, exact=True).wait_for(timeout=15000)
    navigation = page.get_by_test_id("stRadioGroup")
    navigation.wait_for(timeout=15000)
    return navigation


def test_streamlit_homepage_loads(page):
    navigation = open_app(page)

    assert navigation.get_by_text("Overview", exact=True).is_visible()
    assert navigation.get_by_text("ETL", exact=True).is_visible()
    assert navigation.get_by_text("RAG", exact=True).is_visible()
    assert navigation.get_by_text("Failures", exact=True).is_visible()


def test_rag_page_navigation(page):
    navigation = open_app(page)
    navigation.get_by_text("RAG", exact=True).click()

    page.get_by_text("Upload Text Document").wait_for(timeout=10000)
    page.get_by_text("Ask a Question").wait_for(timeout=10000)


def test_etl_page_navigation(page):
    navigation = open_app(page)
    navigation.get_by_text("ETL", exact=True).click()

    page.get_by_text("Upload CSV").wait_for(timeout=10000)
    page.get_by_text("ETL Runs", exact=True).wait_for(timeout=10000)


def test_agents_page_navigation(page):
    navigation = open_app(page)
    navigation.get_by_text("Agents", exact=True).click()

    page.get_by_text("Agentic Workflow Orchestrator").wait_for(timeout=10000)
