import pandas as pd
import argparse
import ast

from data_processing import process_data
from optimization import optimize_shifts 
from reports import report_by_worker, report_by_shop, report_global
from show_calendar_by_worker import generate_worker_calendar
from show_calendar_by_shop import generate_shop_calendar
from worker_data_processor import process_worker_data
from store_shifts_generator import generate_store_shifts
from config import get_config


def main(input_format='csv'):

    print(f"Input format: {input_format}")

    init_data, workers, stores_data = get_config()

    if input_format == 'json':


        generate_store_shifts()

        process_worker_data(init_data, workers, input_format)

    elif input_format == 'csv':

        process_worker_data(init_data, input_format)

    # Pre-procesamos los datos
    process_data(init_data, stores_data)

    # Cargamos los datos procesados
    df_shifts = pd.read_csv("../intermediate_data/turnos_expandidos.csv")
    df_workers = pd.read_csv("../intermediate_data/trabajadores.csv")

    df_workers["Horas extra disponibles"] = df_workers["Horas extra disponibles"].fillna(0)

    # Convertimos las columnas de días a listas
    # Convertir las columnas de días a listas de enteros
    for col in ["Descanso", "Incapacidad", "Vacaciones"]:
        df_workers[col] = df_workers[col].fillna("").apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) and x.strip().startswith("[") else (
                list(map(int, str(x).split(","))) if str(x).strip() else []
            )
        )


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
    generate_shop_calendar(init_data, stores_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Optimización de horas extra')
    parser.add_argument('--format', type=str, default='json', choices=['csv', 'json'],
                      help='csv o json')
    args = parser.parse_args()
    main(args.format)
