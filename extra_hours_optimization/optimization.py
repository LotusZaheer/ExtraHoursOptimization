import pandas as pd
from pyomo.environ import (Constraint, ConcreteModel, Var, 
                           Binary, NonNegativeReals, 
                           minimize, maximize, 
                           Objective, SolverFactory)


def optimize_shifts(df_turnos, df_empleados):

    # Variables auxiliares
    turnos = df_turnos.index.tolist()
    empleados = df_empleados["Nombre"].tolist()
    dias_mes = df_turnos["Día del mes"].unique()
    tiendas = df_turnos["Nombre Tienda"].unique()

    # Crear el modelo de optimización
    model = ConcreteModel()

    # Variables de decisión
    model.x = Var(turnos, empleados, domain=Binary)


    # Funciones de restricción
    def cubrir_turnos_rule(model, turno):
        # Restricción:
        # cada turno debe ser cubierto por la cantidad necesaria de personas
        return sum(model.x[turno, empleado] for empleado in empleados) == df_turnos.loc[turno, "Cantidad personas (con este turno)"]

    def tienda_trabajo_rule(model, turno, empleado):
        # Restricción:
        # Un empleado solo puede trabajar en turnos de su tienda
        # En caso de que no tenga una tienda asignada, puede trabajar en cualquier tienda
        tienda_turno = df_turnos.loc[turno, "Nombre Tienda"]
        tienda_empleado = df_empleados.loc[df_empleados["Nombre"]
                                        == empleado, "Encargada punto"].values[0]
        if pd.isna(tienda_empleado) or tienda_empleado == tienda_turno:
            return Constraint.Skip
        return model.x[turno, empleado] == 0

    def disponibilidad_rule(model, turno, empleado):
        # Restricción:
        # los empleados no pueden trabajar en días de incapacidad o vacaciones
        dia_turno = df_turnos.loc[turno, "Día del mes"]

        # Obtener los días no disponibles del empleado
        dias_no_disponibles = df_empleados.loc[df_empleados["Nombre"] == empleado, ["Incapacidad", "Vacaciones", "Descanso", ]].values[0]
        dias_no_disponibles = set(sum(dias_no_disponibles, []))

        if dia_turno in dias_no_disponibles:
            # Marcamos el turno como no asignable a este empleado
            return model.x[turno, empleado] == 0
        return Constraint.Skip

    def un_turno_por_dia_rule(model, empleado, dia):
        # Restricción: Un empleado no puede tener más de un turno por día
        turnos_dia = [turno for turno in turnos if df_turnos.loc[turno, "Día del mes"] == dia]
        return sum(model.x[turno, empleado] for turno in turnos_dia) <= 1

    def limite_horas_rule(model, empleado):
        # Restricción:
        # no exceder las horas mensuales
        horas_disponibles = df_empleados.loc[df_empleados["Nombre"]
                                            == empleado, "Cantidad de horas disponibles del mes"].values[0]
        return sum(model.x[turno, empleado] * df_turnos.loc[turno, "Horas turno"] for turno in turnos) <= horas_disponibles


    # Definimos las restricciones
    model.cubrir_turnos = Constraint(turnos, rule=cubrir_turnos_rule)
    model.tienda_trabajo = Constraint(turnos, empleados, rule=tienda_trabajo_rule)
    model.disponibilidad = Constraint(turnos, empleados, rule=disponibilidad_rule) #Dias no disponibles para un empleado
    model.un_turno_por_dia = Constraint(empleados, dias_mes, rule=un_turno_por_dia_rule)
    model.limite_horas = Constraint(empleados, rule=limite_horas_rule)


    def calcular_horas_necesarias_tienda(tienda):
        return sum(
            df_turnos.loc[t, "Horas turno"] * df_turnos.loc[t, "Cantidad personas (con este turno)"]
            for t in turnos if df_turnos.loc[t, "Nombre Tienda"] == tienda
        )

    def calculate_available_hours_store_employees(shop):
        # Obtener los empleados asignados a la tienda
        empleados_tienda = set()
        for t in turnos:
            if df_turnos.loc[t, "Nombre Tienda"] == shop:
                for e in empleados:
                    if model.x[t, e].value == 1:
                        empleados_tienda.add(e)
        
        # Calcular las horas disponibles de estos empleados
        return sum(
            df_empleados.loc[df_empleados["Nombre"] == e, "Cantidad de horas disponibles del mes"].values[0]
            for e in empleados_tienda
        )


    sum_differences = sum(
        (calculate_available_hours_store_employees(shop) - calcular_horas_necesarias_tienda(shop))
        for shop in tiendas
    ) / len(tiendas)

    model.obj = Objective(
        #expr= abs(add_up_available_hours_of_all_employees_in_each_shop - hours_needed_per_shop),
        expr=abs(sum_differences),
        sense=minimize
    )

    solver = SolverFactory("glpk")
    solver.solve(model)

    # Mostrar información por tienda
    print("\nInformación por tienda:")
    suma_total_horas_necesarias = 0
    suma_total_horas_disponibles = 0
    
    for tienda in tiendas:
        # Calcular horas necesarias
        horas_necesarias = calcular_horas_necesarias_tienda(tienda)
        suma_total_horas_necesarias += horas_necesarias
        
        # Obtener empleados asignados
        empleados_tienda = set()
        for t in turnos:
            if df_turnos.loc[t, "Nombre Tienda"] == tienda:
                for e in empleados:
                    if model.x[t, e].value == 1:
                        empleados_tienda.add(e)
        
        # Calcular horas disponibles
        horas_disponibles = sum(
            df_empleados.loc[df_empleados["Nombre"] == e, "Cantidad de horas disponibles del mes"].values[0]
            for e in empleados_tienda
        )
        suma_total_horas_disponibles += horas_disponibles
        
        # Mostrar información de la tienda
        print(f"\n{tienda}:")
        print(f"  Horas necesarias: {horas_necesarias:.2f}")
        print(f"  Empleados asignados: {', '.join(empleados_tienda)}")
        print(f"  Horas disponibles: {horas_disponibles:.2f}")
    
    print(f"\nTotales:")
    print(f"  Total horas necesarias: {suma_total_horas_necesarias:.2f}")
    print(f"  Total horas disponibles: {suma_total_horas_disponibles:.2f}")
    print(f"  Diferencia: {abs(suma_total_horas_disponibles - suma_total_horas_necesarias):.2f}")

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

    """
    # Identificar turnos no asignados
    turnos_asignados = set(df_asignaciones.apply(lambda x: f"{x['Nombre Tienda']}_{x['Día del mes']}_{x['Inicio turno']}", axis=1))
    turnos_todos = set(df_turnos.apply(lambda x: f"{x['Nombre Tienda']}_{x['Día del mes']}_{x['Inicio turno']}", axis=1))
    turnos_no_asignados = turnos_todos - turnos_asignados
    
    print("df_asignaciones")
    print(df_asignaciones)

    # Identificar empleados sin turnos
    empleados_con_turnos = set(df_asignaciones['Nombre'].unique())
    empleados_sin_turnos = set(empleados) - empleados_con_turnos
    
    # Crear reporte de turnos no asignados
    reporte_turnos = []
    for turno in turnos_no_asignados:
        tienda, dia, inicio = turno.split('_')
        turno_info = df_turnos[
            (df_turnos['Nombre Tienda'] == tienda) & 
            (df_turnos['Día del mes'] == int(dia)) & 
            (df_turnos['Inicio turno'] == inicio)
        ].iloc[0]
        reporte_turnos.append({
            'Nombre Tienda': tienda,
            'Día del mes': dia,
            'Inicio turno': inicio,
            'Fin turno': turno_info['Fin turno'],
            'Horas turno': turno_info['Horas turno']
        })
    
    # Guardar reportes
    df_turnos_no_asignados = pd.DataFrame(reporte_turnos)
    df_empleados_sin_turnos = pd.DataFrame({'Nombre': list(empleados_sin_turnos)})

    print("Turnos no asignados")
    print(df_turnos_no_asignados)
    print("Empleados sin turnos")
    print(df_empleados_sin_turnos)

    """

    return df_asignaciones