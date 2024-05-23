import functions_framework
import datetime
from rainFileParser import retrieve_rain_data_for_months, read_daily_data, calculate_days_in_month
from task_queue import create_task

@functions_framework.http
def handle_request(request):
    request_json = request.get_json(silect=True)
    print(f"Request JSON: {request_json}")

    if "isDailyRequest" in request_json and request_json["isDailyRequest"]:
        if request_json["finalized"]:
            year = request_json["year"]
            for month in request_json["months"]:
                days_in_month = calculate_days_in_month(year=year, month=month)
                for day in range(days_in_month):
                    rain_data = read_daily_data(year, month, day, is_final=True)
                    for i in range(0, len(rain_data), 1000):
                        create_task(rain_data[i:i+1000].to_dict(), request_json["returnEndPoint"])

        else:
            rain_data = read_daily_data(request_json["year"], request_json["month"], request_json["day"], is_final=False)
            for i in range(0, len(rain_data), 1000):
                create_task(rain_data[i:i+1000].to_dict(), request_json["returnEndPoint"])
    else:
        rain_data = retrieve_rain_data_for_months(request_json["year"], request_json["months"], request_json["finalized"], request_json["intervalCode"])
        create_task(rain_data.to_dict(), request_json["returnEndPoint"])
    return "OK"