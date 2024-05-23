from rainFileParser import retrieve_monthly_rain_data, retrieve_rain_data_for_months, RainResponse

import csv
from typing import List


def main():
    year = 2022
    months = list(range(1, 3))  # Retrieve data for all months
    finalized = True  # Assuming you want to retrieve the finalized data
    interval_code = 1  # Replace with the appropriate interval code
    rain_data = retrieve_rain_data_for_months(year, months, finalized, interval_code)
    create_csv(rain_data)

def create_csv(rain_data: RainResponse):
    filename = f"rainfall_{rain_data.year}.csv"
    with open(filename, "w", newline="") as csvfile:
        fieldnames = ["Year", "Grid_ID", "Month", "Total_Rainfall_mm"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for month_idx, month_data in enumerate(rain_data.rain_data, start=1):
            for grid_id, grid_rain in month_data.items():
                writer.writerow({
                    "Year": rain_data.year,
                    "Grid_ID": grid_id,
                    "Month": month_idx,
                    "Total_Rainfall_mm": grid_rain.total_rainfall_mm
                })

if __name__ == "__main__":
    main()