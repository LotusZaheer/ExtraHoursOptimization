

import pandas as pd
import holidays
import calendar

dias_semana = {"LU": 0, "MA": 1, "MI": 2, "JU": 3, "VI": 4, "SA": 5, "DO": 6, "FE": 7, "MN": 8}

tienda_valores = {'T_MB': False, 'T_EC': True, 'T_CT': True}


def expand_days(row):
    days = row["Días"].split(", ")
    expanded_rows = []
    for day in days:
        new_row = row.copy()
        new_row["Días"] = day
        expanded_rows.append(new_row)
    return expanded_rows


def obtener_dias_mes(dia_semana, available_holidays, anio=2025, mes=1, pais="CO"):
    num_dia = dias_semana.get(dia_semana)
    if num_dia is None:
        return ""

    ultimo_dia = calendar.monthrange(anio, mes)[1]
    festivos = holidays.country_holidays(pais, years=anio)

    if available_holidays:
        if dia_semana == "FE":
            return ",".join(
                str(dia) for dia in range(1, ultimo_dia + 1)
                if f"{anio}-{mes:02d}-{dia:02d}" in festivos
            )
        else:
            return ",".join(
                str(dia) for dia in range(1, ultimo_dia + 1)
                if calendar.weekday(anio, mes, dia) == num_dia and f"{anio}-{mes:02d}-{dia:02d}" not in festivos
            )
    else:
        return ",".join(
            str(dia) for dia in range(1, ultimo_dia + 1)
            if calendar.weekday(anio, mes, dia) == num_dia
        )


def procesar_datos():

    df = pd.read_csv("../inputs/data.csv")

    df_turnos = pd.DataFrame([row for rows in df.apply(expand_days, axis=1) for row in rows])
    df_turnos.reset_index(drop=True, inplace=True)

    df_turnos["Días del mes"] = df_turnos.apply(lambda row: obtener_dias_mes(row["Días"], tienda_valores.get(row["Nombre Tienda"], True)), axis=1)
    df_turnos = df_turnos[df_turnos["Días del mes"].notna() & (df_turnos["Días del mes"] != "")]

    df_turnos_expandidos = df_turnos.assign(
        **{"Día del mes": df_turnos["Días del mes"].str.split(",")}).explode("Día del mes")
    df_turnos_expandidos = df_turnos_expandidos.dropna(subset=["Día del mes"])
    
    df_turnos_expandidos["Día del mes"] = pd.to_numeric(
        df_turnos_expandidos["Día del mes"], errors="coerce").dropna().astype(int)
    df_turnos_expandidos = df_turnos_expandidos.drop(columns=["Días del mes"])
    
    df_turnos_expandidos.to_csv("../intermediate_data/turnos_expandidos.csv", index=False)