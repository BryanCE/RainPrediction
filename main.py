from rainFileParser import retrieve_monthly_rain_data, retrieve_rain_data_for_months, RainResponse

import csv
from typing import List
import json



def create_csv(rain_data: RainResponse):
    filename = f"rainfall_{rain_data.year}.csv"
    with open(filename, "w", newline="") as csvfile:
        fieldnames = ["Year", "Grid_ID", "Month", "Total_Rainfall_mm"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in rain_data.rain_data:
            gridId = item.grid_id
            for month_data in item.month_data:
                month, total_rainfall_mm = month_data.popitem()
                writer.writerow(
                    {
                        "Year": rain_data.year,
                        "Grid_ID": gridId,
                        "Month": month,
                        "Total_Rainfall_mm": total_rainfall_mm,
                    }
                )

def create_json(rain_data: RainResponse):
    filename = f"rainfall_{rain_data.year}.json"
    data = []

    for item in rain_data.rain_data:
        grid_id = item.grid_id
        month_data = []

        for month_dict in item.month_data:
            month, total_rainfall_mm = list(month_dict.items())[0]
            month_data.append({
                "Month": month,
                "Total_Rainfall_mm": total_rainfall_mm
            })

        data.append({
            "Grid_ID": grid_id,
            "Month_Data": month_data
        })

    with open(filename, "w") as jsonfile:
        json.dump(data, jsonfile, indent=4)

if __name__ == "__main__":
    print("Press x to exit when done.")
    yearToUse = input("Enter the year you want to retrieve data for: ")
    year = int(yearToUse)
    months = list(range(1, 13))  # Retrieve data for all months
    finalized = True  # Assuming you want to retrieve the finalized data
    interval_code = 1  # Replace with the appropriate interval code
    rain_data = retrieve_rain_data_for_months(year, months, finalized, interval_code)
    #create_csv(rain_data)
    create_json(rain_data)
    print("Data has been saved to JSON file, check the project directory for the file.")