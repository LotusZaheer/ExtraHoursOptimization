

import pandas as pd
import calendar
from pyomo.environ import *
import holidays
import numpy as np

dias_semana = {"LU": 0, "MA": 1, "MI": 2,
               "JU": 3, "VI": 4, "SA": 5, "DO": 6, "FE": 7, "MN": 8}

tienda_valores = {'T_MB': False, 'T_EC': True, 'T_CT': True}

def expand_days(row):
    days = row["Días"].split(", ")
    expanded_rows = []
    for day in days:
        new_row = row.copy()
        new_row["Días"] = day
        expanded_rows.append(new_row)
    return expanded_rows

def obtener_dias_mes(dia_semana, available_holidays, anio=2025, mes=1, pais="CO"):
    num_dia = dias_semana.get(dia_semana)
    if num_dia is None:
        return ""

    ultimo_dia = calendar.monthrange(anio, mes)[1]
    festivos = holidays.country_holidays(pais, years=anio)

    if available_holidays:
        if dia_semana == "FE":
            return ",".join(
                str(dia) for dia in range(1, ultimo_dia + 1)
                if f"{anio}-{mes:02d}-{dia:02d}" in festivos
            )
        else:
            return ",".join(
                str(dia) for dia in range(1, ultimo_dia + 1)
                if calendar.weekday(anio, mes, dia) == num_dia and f"{anio}-{mes:02d}-{dia:02d}" not in festivos
            )
    else:
        return ",".join(
            str(dia) for dia in range(1, ultimo_dia + 1)
            if calendar.weekday(anio, mes, dia) == num_dia
        )

def procesar_datos():

    df = pd.read_csv("../inputs/data.csv")
    df_turnos = pd.DataFrame([row for rows in df.apply(expand_days, axis=1) for row in rows])
    df_turnos.reset_index(drop=True, inplace=True)
    df_turnos["Días del mes"] = df_turnos.apply(lambda row: obtener_dias_mes(row["Días"], tienda_valores.get(row["Nombre Tienda"], True)), axis=1)
    df_turnos = df_turnos[df_turnos["Días del mes"].notna() & (df_turnos["Días del mes"] != "")]
    df_turnos_expandidos = df_turnos.assign(
        **{"Día del mes": df_turnos["Días del mes"].str.split(",")}).explode("Día del mes")
    df_turnos_expandidos = df_turnos_expandidos.dropna(subset=["Día del mes"])
    df_turnos_expandidos["Día del mes"] = pd.to_numeric(
        df_turnos_expandidos["Día del mes"], errors="coerce").dropna().astype(int)
    df_turnos_expandidos = df_turnos_expandidos.drop(columns=["Días del mes"])
    df_turnos_expandidos.to_csv("../intermediate_data/turnos_expandidos.csv", index=False)

def optimizar_turnos(df_turnos, df_empleados):

    # Crear el modelo de optimización
    model = ConcreteModel()

    empleados = df_empleados["Nombre"].tolist()
    turnos = df_turnos.index.tolist()

    # Variables
    model.x = Var(turnos, empleados, domain=Binary)

    # Restricción:
    # cada turno debe ser cubierto por la cantidad necesaria de personas
    def cubrir_turnos_rule(model, t):
        return sum(model.x[t, e] for e in empleados) == df_turnos.loc[t, "Cantidad personas (con este turno)"]

    model.cubrir_turnos = Constraint(turnos, rule=cubrir_turnos_rule)


    # Restricción:
    # Un empleado solo puede trabajar en turnos de su tienda
    # En caso de que no tenga una tienda asignada, puede trabajar en cualquier tienda
    def tienda_trabajo_rule(model, t, e):
        tienda_turno = df_turnos.loc[t, "Nombre Tienda"]
        tienda_empleado = df_empleados.loc[df_empleados["Nombre"]
                                        == e, "Encargada punto"].values[0]
        if pd.isna(tienda_empleado) or tienda_empleado == tienda_turno:
            return Constraint.Skip
        return model.x[t, e] == 0

    model.tienda_trabajo = Constraint(turnos, empleados, rule=tienda_trabajo_rule)


    # Restricción:
    # los empleados no pueden trabajar en días de incapacidad o vacaciones
    def disponibilidad_rule(model, t, e):
        dia_turno = df_turnos.loc[t, "Día del mes"]

        # Obtener los días no disponibles del empleado
        dias_no_disponibles = df_empleados.loc[df_empleados["Nombre"] == e, [
            "Incapacidad", "Vacaciones"]].values[0]

        # Aplanar la lista de días no disponibles
        dias_no_disponibles = set(
            dias_no_disponibles[0] + dias_no_disponibles[1])  # Unir ambas listas

        if dia_turno in dias_no_disponibles:
            return model.x[t, e] == 0
        return Constraint.Skip

    model.disponibilidad = Constraint(turnos, empleados, rule=disponibilidad_rule)


    # Restricción: Un empleado no puede tener más de un turno por día
    def un_turno_por_dia_rule(model, e, d):
        turnos_dia = [t for t in turnos if df_turnos.loc[t, "Día del mes"] == d]
        return sum(model.x[t, e] for t in turnos_dia) <= 1

    dias_mes = df_turnos["Día del mes"].unique()
    model.un_turno_por_dia = Constraint(
        empleados, dias_mes, rule=un_turno_por_dia_rule)


    # Restricción:
    # no exceder las horas mensuales
    def limite_horas_rule(model, e):
        horas_disponibles = df_empleados.loc[df_empleados["Nombre"]
                                            == e, "Cantidad de horas disponibles del mes"].values[0]
        return sum(model.x[t, e] * df_turnos.loc[t, "Horas turno"] for t in turnos) <= horas_disponibles

    model.limite_horas = Constraint(empleados, rule=limite_horas_rule)


    ###########################################################################
    # modelo y par minimizar cantidad de empleados en una tienda
    model.y = Var(empleados, domain=Binary)

    def activar_empleado_rule(model, e):
        return sum(model.x[t, e] for t in turnos) <= model.y[e] * len(turnos)

    model.activar_empleado = Constraint(empleados, rule=activar_empleado_rule)


    model.obj = Objective(
        expr=sum(model.y[e] for e in empleados), sense=minimize)
    ###########################################################################

    # Variable binaria para indicar si un empleado trabaja en una tienda
    model.z = Var(empleados, df_turnos["Nombre Tienda"].unique(), domain=Binary)

    # Restricción: si el empleado tiene al menos un turno en una tienda, z[e, t] = 1
    def asignar_tienda_rule(model, e, t):
        turnos_tienda = [tr for tr in turnos if df_turnos.loc[tr, "Nombre Tienda"] == t]
        return sum(model.x[tr, e] for tr in turnos_tienda) <= model.z[e, t] * len(turnos_tienda)

    model.asignar_tienda = Constraint(empleados, df_turnos["Nombre Tienda"].unique(), rule=asignar_tienda_rule)

    # Minimizar la cantidad de tiendas diferentes por persona
    model.obj = Objective(expr=sum(model.z[e, t] for e in empleados for t in df_turnos["Nombre Tienda"].unique()), sense=minimize)
    ###########################################################################


    # Función objetivo: minimizar la cantidad de turnos sin asignar
    model.obj = Objective(expr=sum(model.x[t, e] for t in turnos for e in empleados), sense=maximize)


    solver = SolverFactory("glpk")
    solver.solve(model)

    # Extraer la solución
    asignaciones = []
    for t in turnos:
        for e in empleados:
            if model.x[t, e].value == 1:
                asignaciones.append({
                    "Nombre": e,
                    "Nombre Tienda": df_turnos.loc[t, "Nombre Tienda"],
                    "Días": df_turnos.loc[t, "Días"],
                    "Hora Inicio punto": df_turnos.loc[t, "Hora Inicio punto"],
                    "Hora Final punto": df_turnos.loc[t, "Hora Final punto"],
                    "Horas Apertura por día": df_turnos.loc[t, "Horas Apertura por día"],
                    "Inicio turno": df_turnos.loc[t, "Inicio turno"],
                    "Fin turno": df_turnos.loc[t, "Fin turno"],
                    "Horas turno": df_turnos.loc[t, "Horas turno"],
                    "Día del mes": df_turnos.loc[t, "Día del mes"]
                })

    # Guardar el resultado
    df_asignaciones = pd.DataFrame(asignaciones)
    df_asignaciones.to_csv("../outputs/asignacion_turnos.csv", index=False)
    return df_asignaciones

def reporte_por_trabajador(df_asignaciones, df_empleados):

    # Calcular horas asignadas por trabajador
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


def main():

    # Procesar los datos
    procesar_datos()

    df_turnos = pd.read_csv("../intermediate_data/turnos_expandidos.csv")
    df_empleados = pd.read_csv("../inputs/trabajadores.csv")

    df_empleados["Incapacidad"] = df_empleados["Incapacidad"].fillna(
        "").apply(lambda x: list(map(int, str(x).split(","))) if x else [])
    df_empleados["Vacaciones"] = df_empleados["Vacaciones"].fillna(
        "").apply(lambda x: list(map(int, str(x).split(","))) if x else [])


    # Optimizar los turnos
    df_asignaciones = optimizar_turnos(df_turnos, df_empleados)


    # Generar el reporte por trabajador
    reporte_por_trabajador(df_asignaciones, df_empleados)

    # Generar el reporte por tienda
    reporte_por_tienda(df_asignaciones, df_empleados)



if __name__ == "__main__":
    main()