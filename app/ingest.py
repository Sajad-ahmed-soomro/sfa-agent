# app/ingest.py
"""
Ingestion + simulator utilities for SFA agent.

Provides:
- generate_hourly_readings(days): produce simulated hourly readings
- a tiny in-memory store to hold readings per household (for integration/testing)
- helpers to add/get/clear readings
"""

from typing import List, Dict, Any, Optional
import datetime
import math
import random
import threading

# -- Constants (same factors as analysis.py) --
DEFAULT_CO2_PER_KWH = 0.527  # kg CO2 per kWh (document in README)

# -- In-memory store --
# Structure: { household_id: [reading, reading, ...] }
_store: Dict[str, List[Dict[str, Any]]] = {}
_store_lock = threading.Lock()


def generate_hourly_readings(days: int = 7) -> List[Dict[str, Any]]:
    """
    Generate simulated hourly sensor readings for `days` days.
    Each reading is a dict:
      {
        "timestamp": "<ISO8601>Z",
        "energy_kwh": float,
        "water_liters": float,
        "gas_m3": float
      }
    """
    readings: List[Dict[str, Any]] = []
    now = datetime.datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    total_hours = max(1, int(days) * 24)
    for h in range(total_hours):
        ts = now - datetime.timedelta(hours=(total_hours - h))
        # Patterned values + randomness (keeps values non-negative)
        energy = round(0.3 + 0.7 * math.sin(h / 24 * 2 * math.pi) + random.uniform(-0.1, 0.15), 3)
        water = round(20 + 5 * math.cos(h / 24 * 2 * math.pi) + random.uniform(-2, 2), 2)
        gas = round(0.05 + 0.02 * (1 if 6 <= (ts.hour % 24) <= 9 else 0) + random.uniform(-0.01, 0.01), 3)

        readings.append({
            "timestamp": ts.isoformat() + "Z",
            "energy_kwh": max(0.0, energy),
            "water_liters": max(0.0, water),
            "gas_m3": max(0.0, gas)
        })
    return readings


# -- Store operations (thread-safe) --
def add_readings(household_id: str, readings: List[Dict[str, Any]]) -> None:
    """
    Add a batch of readings to the in-memory store for a household.
    Appends to existing readings if present.
    """
    if not household_id:
        raise ValueError("household_id must be provided")

    with _store_lock:
        if household_id not in _store:
            _store[household_id] = []
        _store[household_id].extend(readings)


def get_readings(household_id: Optional[str] = None, days: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Get readings for a household. If household_id is None, returns empty list.
    If no stored readings exist for the household, returns simulated data for `days` (default 7).
    If `days` is provided and there are stored readings, the function returns the last `days*24` readings.
    """
    if not household_id:
        return []

    with _store_lock:
        stored = _store.get(household_id, None)

    if stored:
        if days is None:
            return list(stored)
        else:
            needed = days * 24
            return list(stored)[-needed:]
    else:
        # No stored data -> return simulated data
        return generate_hourly_readings(days or 7)


def clear_store() -> None:
    """Clear the in-memory store. Useful for tests."""
    with _store_lock:
        _store.clear()


# --------------------------
# Optional FastAPI router snippet
# --------------------------
# If you want an /ingest endpoint, copy the following into app/main.py
# (or import APIRouter from here). It's commented out so this module stays pure-Python.

"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/ingest", tags=["ingest"])

class IngestPayload(BaseModel):
    household_id: str
    readings: List[Dict[str, Any]]

@router.post("/upload")
def upload_readings(payload: IngestPayload):
    try:
        add_readings(payload.household_id, payload.readings)
        return {"status": "ok", "ingested": len(payload.readings)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
"""

# -- End of file --
