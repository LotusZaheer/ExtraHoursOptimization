
import pandas as pd

from data_processing import process_data
from optimization import optimizar_turnos
from reports import report_by_worker, report_by_shop


def main():

    init_data = {
    'holidays_are_availables': {'T_MB': False, 'T_EC': True, 'T_CT': True},
    'maintenance_days_by_store': {
    #"T_MB": {5,},
    #"T_EC": {20},
        },
    'month': 1,
    'year': 2025,
    'country': "CO"
    }

    # Pre-procesamos los datos
    process_data(init_data)

    # Cargamos los datos procesados
    df_turnos = pd.read_csv("../intermediate_data/turnos_expandidos.csv")
    df_empleados = pd.read_csv("../inputs/trabajadores.csv")

    df_empleados["Horas extra disponibles"] = df_empleados["Horas extra disponibles"].fillna(0)

    # Convertimos las columnas de días a listas
    df_empleados["Descanso"] = df_empleados["Descanso"].fillna(
        "").apply(lambda x: list(map(int, str(x).split(","))) if x else [])
    df_empleados["Incapacidad"] = df_empleados["Incapacidad"].fillna(
        "").apply(lambda x: list(map(int, str(x).split(","))) if x else [])
    df_empleados["Vacaciones"] = df_empleados["Vacaciones"].fillna(
        "").apply(lambda x: list(map(int, str(x).split(","))) if x else [])


    # Optimizamos los turnos
    df_asignaciones = optimizar_turnos(df_turnos, df_empleados)

    # Generamos el reporte por trabajador
    report_by_worker(df_asignaciones, df_empleados)

    # Generamos el reporte por tienda
    report_by_shop(df_asignaciones, df_empleados)



if __name__ == "__main__":
    main()
