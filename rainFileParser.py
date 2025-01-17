import requests
from datetime import datetime, date
from collections import defaultdict
from dataclasses import dataclass, asdict, field
from typing import List, Tuple, Optional
import struct
import gzip
from io import BytesIO
from typing import List, Dict
from threading import Thread
import queue


class MyThread(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._returnVal = None

    def run(self):
        if self._target is not None:
            self._returnVal = self._target(*self._args, **self._kwargs)

    def join(self):
        Thread.join(self)
        return self._returnVal

threads = queue.Queue()
results = []

@dataclass
class RmaDailyRain:
    grid_id: int
    date: datetime
    rain_mm: float
    station: int
    is_final: bool


@dataclass
class RmaMonthlyRain:
    year: int
    month: int
    total_rainfall_mm: float = 0

    def set_total_rainfall_mm(self, rainfall_mm):
        self.total_rainfall_mm = rainfall_mm


@dataclass
class GridRain:
    grid_id: int
    month_data: List[Dict[int, float]] = field(default_factory=list)

    def set_rain_in_month(self, month: int, rainfall_mm: float):
        month_data = {month: rainfall_mm}
        self.month_data.append(month_data)

    def to_dict(self):
        return asdict(self)


@dataclass
class RainResponse:
    year: int
    interval_code: int
    all_data_included: bool
    finalized: bool
    last_rain_date: date
    rain_data: list[GridRain]

    def to_dict(self):
        return {
            "year": self.year,
            "all_data_included": self.all_data_included,
            "finalized": self.finalized,
            "interval_code": self.interval_code,
            "last_rain_date": self.last_rain_date.strftime("%Y-%m-%d"),
            "rain_data": [grid_rain.to_dict() for grid_rain in self.rain_data]
        }




def retrieve_rain_data_for_months(year: int, months: List[int], finalized: bool, interval_code: int):
    rain_by_grid = {}
    all_data_included = True
    last_rain_date_fin = date(year, sorted(months)[0], 1)
    for month in sorted(months):
        all_month_data_included, last_rain_date, rain_data = retrieve_monthly_rain_data(year, month, finalized)
        if last_rain_date is not None:
            last_rain_date_fin = last_rain_date
        all_data_included = all_month_data_included
        for grid_id, month_rain in rain_data.items():
            if grid_id not in rain_by_grid:
                rain_by_grid[grid_id] = GridRain(grid_id)
                rain_by_grid[grid_id].set_rain_in_month(month_rain.month, month_rain.total_rainfall_mm)
            else:
                rain_by_grid[grid_id].set_rain_in_month(month_rain.month, month_rain.total_rainfall_mm)

    return RainResponse(year, interval_code, all_data_included, finalized, last_rain_date_fin, [v for v in rain_by_grid.values()])


def read_daily_data(year: int, month: int, day: int, is_final: bool):
    num_grids = 36000
    month_str = f"{month:02d}"
    day_str = f"{day:02d}"
    folder, type_ = determine_folder_and_type(year, is_final)
        

    url = f"https://ftp.cpc.ncep.noaa.gov/precip/CPC_UNI_PRCP/GAUGE_CONUS/{folder}/{year}/PRCP_CU_GAUGE_V1.0CONUS_0.25deg.lnx.{year}{month_str}{day_str}.{type_}"
#https://ftp.cpc.ncep.noaa.gov/precip/CPC_UNI_PRCP/GAUGE_CONUS/UPDATED/DOCU/CPC_Gauge_Ananalysis_Procedure_final_20210316.pdf
    try:
        data = get_little_endian_data(url, type_)
        rain = [struct.unpack('<f', data[i:i + 4])[0] for i in range(0, num_grids * 4, 4)]
        stnm = [struct.unpack('<f', data[i:i + 4])[0] for i in range(num_grids * 4, 2 * num_grids * 4, 4)]

        daily_rains = [RmaDailyRain(i + 1, datetime(year, month, day), rain[i] / 10, round(stnm[i]), is_final) for i in
                        range(num_grids) if rain[i] >= -100]
        return daily_rains

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving file {url}: {e}")
        return None


def retrieve_monthly_rain_data(year: int, month: int, finalized: bool) -> Tuple[bool, date, dict]:
    global threads
    global results
    all_data_included = True
    days_in_month = calculate_days_in_month(year, month)
    monthly_rain = defaultdict(lambda: RmaMonthlyRain(year, month))
    last_rain_date = None


    for day in range(1, days_in_month + 1):
        thread = MyThread(target=read_daily_data, args=(year, month, day, finalized))
        thread.start()
        threads.put(thread)

    while not threads.empty():
        thread = threads.get()
        results.append(thread.join()) 
    if results is None:
        all_data_included = False
    # Flatten the list of lists
    flattened_results = [daily for daily_list in results for daily in daily_list]
    for daily in flattened_results:
        last_rain_date = date(year, month, day)
        month_rain = monthly_rain[daily.grid_id]
        month_rain.set_total_rainfall_mm(month_rain.total_rainfall_mm + daily.rain_mm)
        monthly_rain[daily.grid_id] = month_rain
    

    return all_data_included, last_rain_date, dict(monthly_rain)


    
def determine_folder_and_type(year: int, is_final: bool) -> Tuple[str, str]:
    if year < 2007:
        return "V1.0", "gz"
    elif year < 2009:
        return "RT", "RT.gz"
    elif year < 2019:
        return "RT", "RT"
    else:
        type_ = "UPDATED" if is_final else "RT"
        return type_, type_


def get_little_endian_data(url: str, type_: str) -> bytes:
    response = requests.get(url, timeout=5)
    response.raise_for_status()

    if type_.endswith("gz"):
        with gzip.open(BytesIO(response.content)) as gzip_file:
            return gzip_file.read()
    else:
        return response.content


def calculate_days_in_month(year: int, month: int) -> int:
    if month == 12:
        next_month = datetime(year + 1, 1, 1)
    else:
        next_month = datetime(year, month + 1, 1)
    return (next_month - datetime(year, month, 1)).days