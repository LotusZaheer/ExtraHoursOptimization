import pandas as pd

from config import get_config
from shifts_data_processor import added_metric_to_shifts
from worker_data_processor import process_worker_data
from shifts_by_moth_processor import process_shifts_by_moth
from optimization import optimize_shifts 
from reports import report_by_worker, report_by_shop, report_global
from show_calendar_by_worker import generate_worker_calendar
from show_calendar_by_shop import generate_shop_calendar





def main():

    init_data, df_workers, df_shifts = get_config()

    added_metric_to_shifts(df_shifts)
    process_worker_data(init_data, df_workers)

    # Pre-procesamos los datos
    process_shifts_by_moth(init_data)

    # Cargamos los datos procesados
    df_shifts = pd.read_csv("../intermediate_data/df_shifts_expanded.csv")
    df_workers = pd.read_csv("../intermediate_data/workers.csv")

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
