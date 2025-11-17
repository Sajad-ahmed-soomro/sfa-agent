from typing import Dict,Any,List
import math
import random
import datetime

CO2_PER_KWH=0.527
def simulate_hourly_readings(days:int=7)->List[Dict[str,any]]:
    "Simulate hourly readings for a number of days"
    readings=[]
    now=datetime.datetime.utcnow().replace(minute=0,second=0,microsecond=0)
    total_hours=days*24
    for h in range(total_hours):
        ts=now-datetime.timedelta(hours=total_hours-h)
        energy = round(0.3 + 0.7 * math.sin(h / 24 * 2 * math.pi) + random.uniform(-0.1, 0.15), 3)  # kWh
        water = round(20 + 5 * math.cos(h / 24 * 2 * math.pi) + random.uniform(-2, 2), 2)  # liters per hour
        gas = round(0.05 + 0.02 * (1 if 6 <= (ts.hour % 24) <= 9 else 0) + random.uniform(-0.01, 0.01), 3)
        readings.append({
            "timestamp":ts.isoformat()+"Z",
            "energy_kwh":max(0.0,energy),
            "water_liters":max(0.0,water),
            "gas_m3":max(0.0,gas),

        })
    return readings

def estimate_co2(energy_kwh:float)->float:
    return round(CO2_PER_KWH*energy_kwh,3)

def efficiency_score(metrics:Dict[str,any])->int:
    energy=metrics.get("energy_kwh",0)
    score = int(max(0, min(100, round(100 - (energy / 200) * 100))))
    return score

def aggregate_readings(readings: List[Dict[str, Any]]) -> Dict[str, Any]:
    total_energy = sum(r.get("energy_kwh", 0) for r in readings)
    total_water = sum(r.get("water_liters", 0) for r in readings)
    total_gas = sum(r.get("gas_m3", 0) for r in readings)
    avg_energy = total_energy / (len(readings) or 1)
    metrics = {
        "energy_kwh_total": round(total_energy, 3),
        "energy_kwh_avg_hour": round(avg_energy, 3),
        "water_liters_total": round(total_water, 2),
        "gas_m3_total": round(total_gas, 3),
    }
    return metrics

def generate_recommendations(metrics:Dict[str,any])->List[Dict[str]]:
    recs=[]
    energy=metrics.get("energy_kwh_total",0)
    avg_hour=metrics.get("energy_kwh_avg_total",0)
    water=metrics.get("water_liters_total",0)
    if avg_hour>0:
        recs.append("High hourly energy usage observed — consider checking heavy appliances or shifting loads to off-peak.")

    else:
        recs.append("Hourly energy usage is reasonable; maintain existing habits.")
    if water > 500 * 7:
        recs.append("Water consumption is high — consider shorter showers and fix any leaks.")
    recs.append("Use appliances during off-peak hours where possible to reduce cost and grid emissions.")
    return recs


def analyze_with_simulator(days: int = 7) -> Dict[str, Any]:
    readings = simulate_hourly_readings(days)
    metrics = aggregate_readings(readings)
    metrics["estimated_co2_kg"] = estimate_co2(metrics["energy_kwh_total"])
    metrics["efficiency_score"] = efficiency_score(metrics)
    recommendations = generate_recommendations(metrics)
    summary = f"Energy usage over last {days} days: {metrics['energy_kwh_total']} kWh (CO2: {metrics['estimated_co2_kg']} kg)."
    return {
        "summary": summary,
        "metrics": metrics,
        "recommendations": recommendations
    }



