import pandas as pd
import calendar

from data_processing import process_data
from optimization import optimize_shifts 
from reports import report_by_worker, report_by_shop, report_global
from show_calendar_by_worker import generate_worker_calendar
from show_calendar_by_shop import generate_shop_calendar
from create_data import process_employees
from test_data_generation import generate_test_data
from config import get_config


def main():

    init_data, workers, _ = get_config()

    generate_test_data()

    process_employees(workers, init_data)

    # Pre-procesamos los datos
    process_data(init_data)

    # Cargamos los datos procesados
    df_shifts = pd.read_csv("../intermediate_data/turnos_expandidos.csv")
    df_workers = pd.read_csv("../intermediate_data/trabajadores.csv")

    df_workers["Horas extra disponibles"] = df_workers["Horas extra disponibles"].fillna(0)

    # Convertimos las columnas de días a listas
    df_workers["Descanso"] = df_workers["Descanso"].fillna(
        "").apply(lambda x: list(map(int, str(x).split(","))) if x else [])
    df_workers["Incapacidad"] = df_workers["Incapacidad"].fillna(
        "").apply(lambda x: list(map(int, str(x).split(","))) if x else [])
    df_workers["Vacaciones"] = df_workers["Vacaciones"].fillna(
        "").apply(lambda x: list(map(int, str(x).split(","))) if x else [])


    # Optimizamos los turnos
    df_assignments = optimize_shifts (df_shifts, df_workers)

    # Generamos el reporte por trabajador
    report_by_worker(df_assignments, df_workers, init_data['total_days_in_month'])

    # Generamos el reporte por tienda
    report_by_shop(df_assignments, df_workers)

    # Generamos el reporte global
    report_global(df_assignments, df_workers, df_shifts)

    # Generamos el calendario por trabajador
    generate_worker_calendar()

    # Generamos el calendario por tienda
    generate_shop_calendar(init_data)


if __name__ == "__main__":
    main()
