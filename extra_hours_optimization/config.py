import calendar

def get_config():
    init_data = {
        'holidays_are_availables': {'T_MB': False, 'T_EC': True, 'T_CT': True},
        'maintenance_days_by_store': {
            "T_EC": [20],
        },
        'month': 1,
        'year': 2025,
        'country': "CO",
        'weekly_hours': 46
    }
    init_data['total_days_in_month'] = calendar.monthrange(init_data['year'], init_data['month'])[1]

    workers = [
        {"nombre": "E_AG", "punto": "T_MB", "vacaciones": []},
        {"nombre": "E_CG"},
        {"nombre": "E_YS", "punto": "T_EC", "vacaciones": [2,3,4,7,8,9,10,11,13,14,15,16,17,18,20]},
        {"nombre": "E_ZC"},
        {"nombre": "E_NJ"},
        {"nombre": "E_LV", "punto": "T_CT"},
        {"nombre": "E_LR", "vacaciones": [25,26]},
        {"nombre": "E_JM"},
        {"nombre": "E_AM"},
        {"nombre": "E_NB", "incapacidades": [7,8,9,10]},
        {"nombre": "E_JR"},
        {"nombre": "E_AQ"},
        {"nombre": "E_AD"}
    ]

    stores_data = [
        {
            "store": "T_MB",
            "opening_hours": {
                "start": 9,
                "end": 18,
                "days": ["LU", "MA", "MI", "JU", "VI", "SA", "DO"]
            },
            "shifts": [
                {"start": 9, "end": 18, "people": 1}
            ]
        },
        {
            "store": "T_EC",
            "opening_hours": {
                "start": 7,
                "end": 20,
                "days": ["LU", "MA", "MI", "JU", "VI", "SA"]
            },
            "shifts": [
                {"start": 7, "end": 15, "people": 1},
                {"start": 12, "end": 20, "people": 1}
            ],
            "sunday": {
                "opening_hours": {
                    "start": 9,
                    "end": 18,
                    "days": ["DO"]
                },
                "shifts": [
                    {"start": 9, "end": 18, "people": 1}
                ]
            }
        },
        {
            "store": "T_CT",
            "opening_hours": {
                "start": 6,
                "end": 20,
                "days": ["LU", "MA", "MI", "JU"]
            },
            "shifts": [
                {"start": 6, "end": 14, "people": 2},
                {"start": 13, "end": 20, "people": 4}
            ],
            "weekend": {
                "opening_hours": {
                    "start": 6,
                    "end": 21,
                    "days": ["VI", "SA"]
                },
                "shifts": [
                    {"start": 6, "end": 14, "people": 2},
                    {"start": 13, "end": 21, "people": 4}
                ]
            },
            "sunday": {
                "opening_hours": {
                    "start": 6,
                    "end": 21,
                    "days": ["DO"]
                },
                "shifts": [
                    {"start": 6, "end": 14, "people": 3},
                    {"start": 13, "end": 21, "people": 5}
                ]
            },
            "holiday": {
                "opening_hours": {
                    "start": 6,
                    "end": 21,
                    "days": ["FE"]
                },
                "shifts": [
                    {"start": 6, "end": 14, "people": 2},
                    {"start": 13, "end": 21, "people": 5}
                ]
            }
        }
    ]

    return init_data, workers, stores_data 