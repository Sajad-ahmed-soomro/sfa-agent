# tests/test_analysis.py
import pytest
from app import analysis

def test_aggregate_readings():
    readings = [
        {"hour": 0, "kwh": 1.0},
        {"hour": 1, "kwh": 2.0},
        {"hour": 2, "kwh": 3.0},
    ]
    metrics = analysis.aggregate_readings(readings)

    assert metrics["energy_kwh_total"] == 6.0
    assert metrics["peak_hour_kwh"] == 3.0
    assert metrics["peak_hour"] == 2
    assert metrics["avg_kwh"] == pytest.approx(2.0)


def test_estimate_co2():
    co2 = analysis.estimate_co2(10.0)
    assert co2 > 0
    assert isinstance(co2, float)


def test_efficiency_score():
    metrics = {
        "energy_kwh_total": 100,
        "avg_kwh": 2.5,
    }
    score = analysis.efficiency_score(metrics)

    assert 0 <= score <= 100


def test_generate_recommendations():
    metrics = {
        "energy_kwh_total": 40,
        "avg_kwh": 1.2,
        "peak_hour": 5,
        "peak_hour_kwh": 3.5
    }
    recs = analysis.generate_recommendations(metrics)

    assert isinstance(recs, list)
    assert len(recs) > 0
