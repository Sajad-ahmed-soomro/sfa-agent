# scripts/simulate_data.py
"""
Utility script for generating sample consumption data.
"""

import argparse
from app.ingest import generate_hourly_readings

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=7, help="Number of days")
    args = parser.parse_args()

    readings = generate_hourly_readings(args.days)

    print(f"Generated {len(readings)} data points:")
    for r in readings[:24]:
        print(r)

if __name__ == "__main__":
    main()
