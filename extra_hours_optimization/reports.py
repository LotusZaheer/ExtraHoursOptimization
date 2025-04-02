import numpy as np

def report_by_worker(df_assignments, df_workers, total_days_in_month):

    df_hours_per_worker = df_assignments.groupby(
        "Nombre")[["Horas turno", ]].sum().reset_index()

    df_hours_per_worker = df_hours_per_worker.merge(
        df_workers[["Nombre", "Cantidad de horas disponibles del mes", "Vacaciones", "Incapacidad"]],
        on="Nombre",
        how="left"
    )

    df_hours_per_worker["Vacaciones"] = df_hours_per_worker["Vacaciones"].apply(lambda x: eval(x) if isinstance(x, str) else x)
    df_hours_per_worker["Incapacidad"] = df_hours_per_worker["Incapacidad"].apply(lambda x: eval(x) if isinstance(x, str) else x)

    df_hours_per_worker["Productividad (%)"] = (
        (df_hours_per_worker["Horas turno"] ) /
        df_hours_per_worker["Cantidad de horas disponibles del mes"]
    ) * 100

    df_shops_per_worker = df_assignments.groupby("Nombre")["Nombre Tienda"].nunique().reset_index()
    df_shops_per_worker.rename(columns={"Nombre Tienda": "Cantidad de tiendas asignadas"}, inplace=True)

    df_shops_list = df_assignments.groupby("Nombre")["Nombre Tienda"].unique().reset_index()
    df_shops_list.rename(columns={"Nombre Tienda": "Lista de tiendas asignadas"}, inplace=True)
    df_shops_list["Lista de tiendas asignadas"] = df_shops_list["Lista de tiendas asignadas"].apply(lambda x: x.tolist() if isinstance(x, np.ndarray) else x)

    df_worked_days = df_assignments.groupby("Nombre")["Día del mes"].unique().reset_index()
    df_worked_days.rename(columns={"Día del mes": "Lista de días trabajados"}, inplace=True)
    df_worked_days["Días trabajados"] = df_worked_days["Lista de días trabajados"].apply(len)
    df_worked_days["Lista de días trabajados"] = df_worked_days["Lista de días trabajados"].apply(lambda x: x.tolist() if isinstance(x, np.ndarray) else x).apply(lambda x: sorted(x) if isinstance(x, list) else x)

    df_hours_per_worker = df_hours_per_worker.merge(df_shops_per_worker, on="Nombre", how="left")
    df_hours_per_worker = df_hours_per_worker.merge(df_shops_list, on="Nombre", how="left")
    df_hours_per_worker = df_hours_per_worker.merge(df_worked_days, on="Nombre", how="left")

    df_hours_per_worker["Días de descanso"] = (
        total_days_in_month 
        - df_hours_per_worker["Días trabajados"]
        - df_hours_per_worker["Vacaciones"].apply(len)
        - df_hours_per_worker["Incapacidad"].apply(len)
    )

    df_hours_per_worker["Lista de días descanso"] = df_hours_per_worker.apply(
        lambda row: list(set(range(1, total_days_in_month  + 1)) - set(row["Lista de días trabajados"]) - set(row["Vacaciones"]) - set(row["Incapacidad"])),
        axis=1
    ).apply(lambda x: sorted(x) if isinstance(x, list) else x)


    df_hours_per_worker["Días de vacaciones"] = df_hours_per_worker["Vacaciones"].apply(len)
    df_hours_per_worker["Lista de días vacaciones"] = df_hours_per_worker["Vacaciones"].apply(lambda x: sorted(x) if isinstance(x, list) else x)

    df_hours_per_worker["Días de incapacidad"] = df_hours_per_worker["Incapacidad"].apply(len)
    df_hours_per_worker["Lista de días incapacidad"] = df_hours_per_worker["Incapacidad"].apply(lambda x: sorted(x) if isinstance(x, list) else x)

    df_hours_per_worker.drop(columns=["Vacaciones", "Incapacidad"], inplace=True)

    df_hours_per_worker.to_csv("../outputs/horas_por_trabajador.csv", index=False)

    print("Horas asignadas y productividad por trabajador con métricas adicionales")
    print(df_hours_per_worker.head())


def report_by_shop(df_assignments, df_workers):
    """
    Genera un reporte detallado por tienda incluyendo horas requeridas y disponibles.
    
    Args:
        df_assignments (pd.DataFrame): DataFrame con las asignaciones de turnos
        df_workers (pd.DataFrame): DataFrame con información de los trabajadores
    """
    # Calcular horas trabajadas por tienda
    df_hours_per_shop = df_assignments.groupby("Nombre Tienda")[["Horas turno", ]].sum().reset_index()
    df_hours_per_shop.rename(columns={"Horas turno": "Horas trabajadas"}, inplace=True)

    # Calcular empleados por tienda
    df_workers_per_shop = df_assignments.groupby("Nombre Tienda")["Nombre"].nunique().reset_index()
    df_workers_per_shop.rename(columns={"Nombre": "Cantidad de trabajadores"}, inplace=True)

    # Lista de trabajadores por tienda
    df_worker_list = df_assignments.groupby("Nombre Tienda")["Nombre"].unique().reset_index()
    df_worker_list.rename(columns={"Nombre": "Lista de trabajadores"}, inplace=True)
    df_worker_list["Lista de trabajadores"] = df_worker_list["Lista de trabajadores"].apply(lambda x: x.tolist() if isinstance(x, np.ndarray) else x)

    # Días trabajados por tienda
    df_worked_days = df_assignments.groupby("Nombre Tienda")["Día del mes"].nunique().reset_index()
    df_worked_days.rename(columns={"Día del mes": "Días trabajados"}, inplace=True)

    # Calcular horas disponibles por tienda y por empleado
    def get_worker_hours_info(workers_list):
        hours_info = []
        total_hours = 0
        for worker in workers_list:
            hours = df_workers.loc[df_workers["Nombre"] == worker, "Cantidad de horas disponibles del mes"].values[0]
            total_hours += hours
            hours_info.append(f"{worker}: {hours:.2f} horas")
        return hours_info, total_hours

    df_worker_list["Horas por empleado"] = df_worker_list["Lista de trabajadores"].apply(lambda x: get_worker_hours_info(x)[0])
    df_worker_list["Horas disponibles"] = df_worker_list["Lista de trabajadores"].apply(lambda x: get_worker_hours_info(x)[1])

    # Combinar todos los datos
    df_shop_report = df_hours_per_shop.merge(df_workers_per_shop, on="Nombre Tienda", how="left")
    df_shop_report = df_shop_report.merge(df_worker_list, on="Nombre Tienda", how="left")
    df_shop_report = df_shop_report.merge(df_worked_days, on="Nombre Tienda", how="left")

    df_shop_report.to_csv("../outputs/horas_por_tienda.csv", index=False)
    
    print("\nReporte de horas y métricas por tienda")
    print("=====================================")
    for _, row in df_shop_report.iterrows():
        print(f"\nTienda: {row['Nombre Tienda']}")
        print(f"  Horas trabajadas: {row['Horas trabajadas']:.2f}")
        print(f"  Horas disponibles totales: {row['Horas disponibles']:.2f}")
        print(f"  Cantidad de trabajadores: {row['Cantidad de trabajadores']}")
        print(f"  Días trabajados: {row['Días trabajados']}")
        print("\n  Horas disponibles por empleado:")
        #for hours_info in row['Horas por empleado']:
        #    print(f"    {hours_info}")

def report_global(df_assignments, df_workers, df_shifts):
    """
    Genera un reporte global con métricas generales del sistema.
    
    Args:
        df_assignments (pd.DataFrame): DataFrame con las asignaciones de turnos
        df_workers (pd.DataFrame): DataFrame con información de los trabajadores
        df_shifts (pd.DataFrame): DataFrame con información de los turnos
    """
    print("\nReporte Global del Sistema")
    print("=========================")
    
    # Identificar empleados sin horas asignadas
    empleados_con_horas = set(df_assignments['Nombre'].unique())
    empleados_sin_horas = set(df_workers['Nombre']) - empleados_con_horas
    
    if empleados_sin_horas:
        print("\nEmpleados sin horas asignadas:")
        print("-----------------------------")
        for empleado in sorted(empleados_sin_horas):
            print(f"- {empleado}")
    else:
        print("\nTodos los empleados tienen horas asignadas.")
    
    # Identificar turnos sin asignar
    turnos_asignados = set(df_assignments.apply(lambda x: f"{x['Nombre Tienda']}_{x['Día del mes']}_{x['Inicio turno']}", axis=1))
    turnos_todos = set(df_shifts.apply(lambda x: f"{x['Nombre Tienda']}_{x['Día del mes']}_{x['Inicio turno']}", axis=1))
    turnos_sin_asignar = turnos_todos - turnos_asignados
    
    if turnos_sin_asignar:
        print("\nTurnos sin asignar:")
        print("------------------")
        for turno in sorted(turnos_sin_asignar):
            tienda, dia, inicio = turno.split('_')
            turno_info = df_shifts[
                (df_shifts['Nombre Tienda'] == tienda) & 
                (df_shifts['Día del mes'] == int(dia)) & 
                (df_shifts['Inicio turno'] == inicio)
            ].iloc[0]
            print(f"- Tienda: {tienda}, Día: {dia}, Horario: {inicio} - {turno_info['Fin turno']}")
    else:
        print("\nTodos los turnos están asignados.")