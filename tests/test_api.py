# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_sfa_agent_basic():
    payload = {
        "messages": [
            {"role": "user", "content": "Analyze last 3 days energy usage"}
        ]
    }

    res = client.post("/agent/run", json=payload)
    assert res.status_code == 200

    data = res.json()
    assert "message" in data
    assert "metrics" in data
    assert "recommendations" in data


def test_sfa_agent_custom_readings():
    payload = {
        "messages": [{"role": "user", "content": "Analyze"}],
        "readings": [
            {"hour": 0, "kwh": 1},
            {"hour": 1, "kwh": 1.5},
            {"hour": 2, "kwh": 2},
        ]
    }

    res = client.post("/agent/run", json=payload)
    assert res.status_code == 200

    data = res.json()
    assert data["metrics"]["energy_kwh_total"] == 4.5
