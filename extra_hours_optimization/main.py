import pandas as pd

from data_processing import process_data
from optimization import optimize_shifts 
from reports import report_by_worker, report_by_shop, report_global


def main():

    init_data = {
    'holidays_are_availables': {'T_MB': False, 'T_EC': True, 'T_CT': True},
    'maintenance_days_by_store': {
    #"T_MB": {5,},
    "T_EC": {20},
        },
    'month': 1,
    'year': 2025,
    'country': "CO"
    }
    total_days_in_month=31

    # Pre-procesamos los datos
    process_data(init_data)

    # Cargamos los datos procesados
    df_shifts = pd.read_csv("../intermediate_data/turnos_expandidos.csv")
    df_workers = pd.read_csv("../inputs/trabajadores.csv")

    df_workers["Horas extra disponibles"] = df_workers["Horas extra disponibles"].fillna(0)

    # Convertimos las columnas de días a listas
    df_workers["Descanso"] = df_workers["Descanso"].fillna(
        "").apply(lambda x: list(map(int, str(x).split(","))) if x else [])
    df_workers["Incapacidad"] = df_workers["Incapacidad"].fillna(
        "").apply(lambda x: list(map(int, str(x).split(","))) if x else [])
    df_workers["Vacaciones"] = df_workers["Vacaciones"].fillna(
        "").apply(lambda x: list(map(int, str(x).split(","))) if x else [])


    # Optimizamos los turnos
    df_assignments = optimize_shifts (df_shifts, df_workers.head(12))

    # Generamos el reporte por trabajador
    report_by_worker(df_assignments, df_workers, total_days_in_month)

    # Generamos el reporte por tienda
    report_by_shop(df_assignments)

    # Generamos el reporte global
    report_global(df_assignments, df_workers, df_shifts)



if __name__ == "__main__":
    main()
