import requests


SERVICE_URLS = [
    "http://localhost:8000/health",
    "http://localhost:8001/health",
    "http://localhost:8002/health",
    "http://localhost:8003/health",
]


def test_services_health_endpoints():
    for url in SERVICE_URLS:
        response = requests.get(url, timeout=10)

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"