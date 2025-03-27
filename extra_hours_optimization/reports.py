
import numpy as np

def reporte_por_trabajador(df_asignaciones, df_empleados):

    df_horas_por_trabajador = df_asignaciones.groupby(
        "Nombre")["Horas turno"].sum().reset_index()

    df_horas_por_trabajador = df_horas_por_trabajador.merge(
        df_empleados[["Nombre", "Cantidad de horas disponibles del mes", "Vacaciones", "Incapacidad"]],
        on="Nombre",
        how="left"
    )

    df_horas_por_trabajador["Vacaciones"] = df_horas_por_trabajador["Vacaciones"].apply(lambda x: eval(x) if isinstance(x, str) else x)
    df_horas_por_trabajador["Incapacidad"] = df_horas_por_trabajador["Incapacidad"].apply(lambda x: eval(x) if isinstance(x, str) else x)

    df_horas_por_trabajador["Productividad (%)"] = (
        df_horas_por_trabajador["Horas turno"] /
        df_horas_por_trabajador["Cantidad de horas disponibles del mes"]
    ) * 100

    df_tiendas_por_trabajador = df_asignaciones.groupby("Nombre")["Nombre Tienda"].nunique().reset_index()
    df_tiendas_por_trabajador.rename(columns={"Nombre Tienda": "Cantidad de tiendas asignadas"}, inplace=True)

    df_tiendas_lista = df_asignaciones.groupby("Nombre")["Nombre Tienda"].unique().reset_index()
    df_tiendas_lista.rename(columns={"Nombre Tienda": "Lista de tiendas asignadas"}, inplace=True)
    df_tiendas_lista["Lista de tiendas asignadas"] = df_tiendas_lista["Lista de tiendas asignadas"].apply(lambda x: x.tolist() if isinstance(x, np.ndarray) else x)

    df_dias_trabajados = df_asignaciones.groupby("Nombre")["Día del mes"].unique().reset_index()
    df_dias_trabajados.rename(columns={"Día del mes": "Lista de días trabajados"}, inplace=True)
    df_dias_trabajados["Días trabajados"] = df_dias_trabajados["Lista de días trabajados"].apply(len)
    df_dias_trabajados["Lista de días trabajados"] = df_dias_trabajados["Lista de días trabajados"].apply(lambda x: x.tolist() if isinstance(x, np.ndarray) else x).apply(lambda x: sorted(x) if isinstance(x, list) else x)

    df_horas_por_trabajador = df_horas_por_trabajador.merge(df_tiendas_por_trabajador, on="Nombre", how="left")
    df_horas_por_trabajador = df_horas_por_trabajador.merge(df_tiendas_lista, on="Nombre", how="left")
    df_horas_por_trabajador = df_horas_por_trabajador.merge(df_dias_trabajados, on="Nombre", how="left")

    dias_totales_mes = 31
    df_horas_por_trabajador["Días de descanso"] = (
        dias_totales_mes
        - df_horas_por_trabajador["Días trabajados"]
        - df_horas_por_trabajador["Vacaciones"].apply(len)
        - df_horas_por_trabajador["Incapacidad"].apply(len)
    )

    df_horas_por_trabajador["Lista de días descanso"] = df_horas_por_trabajador.apply(
        lambda row: list(set(range(1, dias_totales_mes + 1)) - set(row["Lista de días trabajados"]) - set(row["Vacaciones"]) - set(row["Incapacidad"])),
        axis=1
    ).apply(lambda x: sorted(x) if isinstance(x, list) else x)


    df_horas_por_trabajador["Días de vacaciones"] = df_horas_por_trabajador["Vacaciones"].apply(len)
    df_horas_por_trabajador["Lista de días vacaciones"] = df_horas_por_trabajador["Vacaciones"].apply(lambda x: sorted(x) if isinstance(x, list) else x)

    df_horas_por_trabajador["Días de incapacidad"] = df_horas_por_trabajador["Incapacidad"].apply(len)
    df_horas_por_trabajador["Lista de días incapacidad"] = df_horas_por_trabajador["Incapacidad"].apply(lambda x: sorted(x) if isinstance(x, list) else x)

    df_horas_por_trabajador.drop(columns=["Vacaciones", "Incapacidad"], inplace=True)

    df_horas_por_trabajador.to_csv("../outputs/horas_por_trabajador.csv", index=False)

    print("Horas asignadas y productividad por trabajador con métricas adicionales")
    print(df_horas_por_trabajador.head())

def reporte_por_tienda(df_asignaciones, df_empleados):

    # Calcular horas asignadas por tienda
    df_horas_por_tienda = df_asignaciones.groupby(
        "Nombre Tienda")["Horas turno"].sum().reset_index()
    df_horas_por_tienda.to_csv("../outputs/horas_por_tienda.csv", index=False)

    print("Horas asignadas por tienda")
    print(df_horas_por_tienda.head())
