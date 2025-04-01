import pandas as pd
import holidays
import calendar

days_of_week = {"LU": 0, "MA": 1, "MI": 2, "JU": 3, "VI": 4, "SA": 5, "DO": 6, "FE": 7, "MN": 8}


def expand_days(row):
    days = row["Días"].split(", ")
    expanded_rows = []
    for day in days:
        new_row = row.copy()
        new_row["Días"] = day
        expanded_rows.append(new_row)
    return expanded_rows


def get_days_of_month(day_of_week, available_holidays, maintenance_days, year=2025, month=1, country="CO"):
    day_num = days_of_week.get(day_of_week)
    if day_num is None:
        return ""

    last_day = calendar.monthrange(year, month)[1]
    holidays_list = holidays.country_holidays(country, years=year)

    if available_holidays:
        if day_of_week == "FE":
            return ",".join(
                str(day) for day in range(1, last_day + 1)
                if f"{year}-{month:02d}-{day:02d}" in holidays_list
            )
        else:
            return ",".join(
                str(day) for day in range(1, last_day + 1)
                if calendar.weekday(year, month, day) == day_num and f"{year}-{month:02d}-{day:02d}" not in holidays_list
                and day not in maintenance_days
            )
    else:
        return ",".join(
            str(day) for day in range(1, last_day + 1)
            if calendar.weekday(year, month, day) == day_num
            and day not in maintenance_days
        )


def process_data(init_data):

    holidays_are_availables = init_data['holidays_are_availables']
    month = init_data['month']
    year = init_data['year']
    country = init_data['country']
    maintenance_days_by_store = init_data['maintenance_days_by_store']

    df = pd.read_csv("../intermediate_data/data.csv")

    df_shifts = pd.DataFrame([row for rows in df.apply(expand_days, axis=1) for row in rows])
    df_shifts.reset_index(drop=True, inplace=True)

    df_shifts["Días del mes"] = df_shifts.apply(lambda row: get_days_of_month(row["Días"],
                                                                                 holidays_are_availables.get(row["Nombre Tienda"], True),
                                                                                 maintenance_days_by_store.get(row["Nombre Tienda"], set()),
                                                                                 year=year,
                                                                                 month=month,
                                                                                 country=country
                                                                                ), axis=1)
    df_shifts = df_shifts[df_shifts["Días del mes"].notna() & (df_shifts["Días del mes"] != "")]

    df_shifts_expanded = df_shifts.assign(
        **{"Día del mes": df_shifts["Días del mes"].str.split(",")}).explode("Día del mes")
    df_shifts_expanded = df_shifts_expanded.dropna(subset=["Día del mes"])
    
    df_shifts_expanded["Día del mes"] = pd.to_numeric(
        df_shifts_expanded["Día del mes"], errors="coerce").dropna().astype(int)
    df_shifts_expanded = df_shifts_expanded.drop(columns=["Días del mes"])
    
    df_shifts_expanded.to_csv("../intermediate_data/turnos_expandidos.csv", index=False)
