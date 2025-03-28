import pandas as pd
from pyomo.environ import (Constraint, ConcreteModel, Var, 
                           Binary, NonNegativeReals, 
                           minimize, maximize, 
                           Objective, SolverFactory)


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
            "Incapacidad", "Vacaciones", "Descanso", ]].values[0]

        # Aplanar la lista de días no disponibles
        dias_no_disponibles = set(sum(dias_no_disponibles, []))

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

    ###########################################################################
    # Variable binaria para indicar si una tienda tiene empleados asignados
    model.w = Var(df_turnos["Nombre Tienda"].unique(), domain=Binary)

    # Restricción: si una tienda tiene al menos un empleado asignado, w[t] = 1
    def activar_tienda_rule(model, t):
        turnos_tienda = [tr for tr in turnos if df_turnos.loc[tr, "Nombre Tienda"] == t]
        return sum(model.x[tr, e] for tr in turnos_tienda for e in empleados) <= model.w[t] * len(turnos_tienda) * len(empleados)

    model.activar_tienda = Constraint(df_turnos["Nombre Tienda"].unique(), rule=activar_tienda_rule)

    # Minimizar la cantidad de tiendas con empleados asignados
    model.obj = Objective(expr=sum(model.w[t] for t in df_turnos["Nombre Tienda"].unique()), sense=minimize)
    ###########################################################################

    # Función objetivo: minimizar la cantidad de turnos sin asignar

    cal_hours = sum(model.x[t, e] for t in turnos for e in empleados)  

    model.obj = Objective(
        expr= cal_hours ,
        sense=maximize
    )


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
                    "Día del mes": df_turnos.loc[t, "Día del mes"],
                })

    # Guardar el resultado
    df_asignaciones = pd.DataFrame(asignaciones)
    df_asignaciones.to_csv("../outputs/asignacion_turnos.csv", index=False)
    return df_asignaciones