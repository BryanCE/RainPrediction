from rainFileParser import retrieve_monthly_rain_data, retrieve_rain_data_for_months

import csv
from datetime import datetime

if __name__ == "__main__":
    # Specify the years and months you want to retrieve data for
    years_and_months = [
        (2020, [1, 2]),
    ]
    finalized = False  # Set to True if you want to retrieve finalized data
    interval_code = 1  # Specify the interval code (e.g., 1 for daily data)

    # CSV file to store all data
    csv_filename = f"rain_data_multiple_{years_and_months}.csv"

    # Open the CSV file in append mode
    with open(csv_filename, mode='a', newline='') as csv_file:
        fieldnames = ['year', 'month', 'grid_id', 'total_rainfall_mm']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # Write the header if the file is new
        if csv_file.tell() == 0:
            writer.writeheader()

        # Retrieve and save rain data for each year and month
        for year, months in years_and_months:
            rain_response = retrieve_rain_data_for_months(year, months, finalized, interval_code)

            for grid_rain in rain_response.rain_data:
                for month in months:
                    writer.writerow({
                        'year': year,
                        'month': month,
                        'grid_id': grid_rain.grid_id,
                        'total_rainfall_mm': grid_rain.total_rainfall_mm
                    })

    print(f"Rain data for multiple years and months saved to {csv_filename}")