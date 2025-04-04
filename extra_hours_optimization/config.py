import calendar
import pandas as pd

def get_config():

    init_data = {
        'month': 1,
        'year': 2025,
        'country': "CO",
        'weekly_hours': 46,
        'stores_data': [
                {
                    "store": "T_MB",
                    "holidays_available": False,
                    "maintenance_days": [],
                },
                {
                    "store": "T_EC",
                    "holidays_available": True,
                    "maintenance_days": [20],
                },
                {
                    "store": "T_CT",
                    "holidays_available": True,
                    "maintenance_days": [],
                }
            ]
    }

    init_data['total_days_in_month'] = calendar.monthrange(init_data['year'], init_data['month'])[1]

    df_workers = pd.read_csv("../inputs/workers.csv")
    df_shifts = pd.read_csv("../inputs/shift_by_store.csv")

    return init_data, df_workers, df_shifts