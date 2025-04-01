
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


def report_by_shop(df_assignments):

    df_hours_per_shop = df_assignments.groupby("Nombre Tienda")[["Horas turno", ]].sum().reset_index()

    df_workers_per_shop = df_assignments.groupby("Nombre Tienda")["Nombre"].nunique().reset_index()
    df_workers_per_shop.rename(columns={"Nombre": "Cantidad de trabajadores"}, inplace=True)

    df_worker_list = df_assignments.groupby("Nombre Tienda")["Nombre"].unique().reset_index()
    df_worker_list.rename(columns={"Nombre": "Lista de trabajadores"}, inplace=True)
    df_worker_list["Lista de trabajadores"] = df_worker_list["Lista de trabajadores"].apply(lambda x: x.tolist() if isinstance(x, np.ndarray) else x)

    df_worked_days = df_assignments.groupby("Nombre Tienda")["Día del mes"].nunique().reset_index()
    df_worked_days.rename(columns={"Día del mes": "Días trabajados"}, inplace=True)

    df_shop_report = df_hours_per_shop.merge(df_workers_per_shop, on="Nombre Tienda", how="left")
    df_shop_report = df_shop_report.merge(df_worker_list, on="Nombre Tienda", how="left")
    df_shop_report = df_shop_report.merge(df_worked_days, on="Nombre Tienda", how="left")

    df_shop_report.to_csv("../outputs/horas_por_tienda.csv", index=False)
    
    print("Reporte de horas y métricas por tienda")
    print(df_shop_report.head())