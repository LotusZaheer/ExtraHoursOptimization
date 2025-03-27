
import pandas as pd

from data_processing import procesar_datos
from optimization import optimizar_turnos
from reports import reporte_por_trabajador, reporte_por_tienda


def main():

    # Pre-procesamos los datos
    procesar_datos()

    # Cargamos los datos procesados
    df_turnos = pd.read_csv("../intermediate_data/turnos_expandidos.csv")
    df_empleados = pd.read_csv("../inputs/trabajadores.csv")

    # Convertimos las columnas de días a listas
    df_empleados["Incapacidad"] = df_empleados["Incapacidad"].fillna(
        "").apply(lambda x: list(map(int, str(x).split(","))) if x else [])
    df_empleados["Vacaciones"] = df_empleados["Vacaciones"].fillna(
        "").apply(lambda x: list(map(int, str(x).split(","))) if x else [])


    # Optimizamos los turnos
    df_asignaciones = optimizar_turnos(df_turnos, df_empleados)

    # Generamos el reporte por trabajador
    reporte_por_trabajador(df_asignaciones, df_empleados)

    # Generamos el reporte por tienda
    reporte_por_tienda(df_asignaciones, df_empleados)



if __name__ == "__main__":
    main()
