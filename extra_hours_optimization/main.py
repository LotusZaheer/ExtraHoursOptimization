import pandas as pd

from data_processing import process_data
from optimization import optimizar_turnos
from reports import report_by_worker, report_by_shop
from logger import setup_logger
from config import Config
logger = setup_logger()

def main():
    logger.info("Iniciando proceso de optimización de horas extra")

    # Cargamos la configuración
    config = Config()

    init_data = {
        'holidays_are_availables': config.holidays_availability,
        'maintenance_days_by_store': config.maintenance_days,
        'month': config.month,
        'year': config.year,
        'country': config.country
    }

    # Pre-procesamos los datos
    logger.info("Iniciando pre-procesamiento de datos")
    process_data(init_data)
    logger.info("Pre-procesamiento de datos completado")

    # Cargamos los datos procesados
    logger.info("Cargando datos procesados")
    df_turnos = pd.read_csv("../intermediate_data/turnos_expandidos.csv")
    df_empleados = pd.read_csv("../inputs/trabajadores.csv")
    logger.info(f"Datos cargados: {len(df_turnos)} turnos, {len(df_empleados)} empleados")

    df_empleados["Horas extra disponibles"] = df_empleados["Horas extra disponibles"].fillna(0)

    # Convertimos las columnas de días a listas
    logger.info("Procesando datos de empleados")
    df_empleados["Descanso"] = df_empleados["Descanso"].fillna(
        "").apply(lambda x: list(map(int, str(x).split(","))) if x else [])
    df_empleados["Incapacidad"] = df_empleados["Incapacidad"].fillna(
        "").apply(lambda x: list(map(int, str(x).split(","))) if x else [])
    df_empleados["Vacaciones"] = df_empleados["Vacaciones"].fillna(
        "").apply(lambda x: list(map(int, str(x).split(","))) if x else [])

    # Optimizamos los turnos
    logger.info("Iniciando optimización de turnos")
    df_asignaciones = optimizar_turnos(df_turnos, df_empleados)
    logger.info(f"Optimización completada: {len(df_asignaciones)} asignaciones generadas")

    # Generamos el reporte por trabajador
    logger.info("Generando reporte por trabajador")
    report_by_worker(df_asignaciones, df_empleados)
    logger.info("Reporte por trabajador generado")

    # Generamos el reporte por tienda
    logger.info("Generando reporte por tienda")
    report_by_shop(df_asignaciones, df_empleados)
    logger.info("Reporte por tienda generado")
    logger.info("Proceso completado exitosamente")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Error durante la ejecución: {str(e)}", exc_info=True)
        raise
