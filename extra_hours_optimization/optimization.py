import pandas as pd
from pyomo.environ import (Constraint, ConcreteModel, Var, 
                           Binary, NonNegativeReals, 
                           minimize, maximize, 
                           Objective, SolverFactory)


def optimize_shifts(df_shifts, df_workers):

    # Variables auxiliares
    turnos = df_shifts.index.tolist()
    workers = df_workers["Nombre"].tolist()
    days_in_month = df_shifts["Día del mes"].unique()
    tiendas = df_shifts["Nombre Tienda"].unique()

    # Crear el modelo de optimización
    model = ConcreteModel()

    # Variables de decisión
    model.x = Var(turnos, workers, domain=Binary)


    # Funciones de restricción
    def cover_shifts_rule(model, shift):
        # Restricción:
        # cada turno debe ser cubierto por la cantidad necesaria de personas
        return sum(model.x[shift, worker] for worker in workers) == df_shifts.loc[shift, "Cantidad personas (con este turno)"]

    def store_work_rule(model, shift, worker):
        # Restricción:
        # Un empleado solo puede trabajar en turnos de su tienda
        # En caso de que no tenga una tienda asignada, puede trabajar en cualquier tienda
        store_shift = df_shifts.loc[shift,"Nombre Tienda"]
        store_worker = df_workers.loc[df_workers["Nombre"]
                                        == worker, "Encargada punto"].values[0]
        if pd.isna(store_worker) or store_worker == store_shift:
            return Constraint.Skip
        return model.x[shift, worker] == 0

    def availability_rule(model, shift, worker):
        # Restricción:
        # los empleados no pueden trabajar en días de incapacidad o vacaciones
        shift_day = df_shifts.loc[shift, "Día del mes"]

        # Obtener los días no disponibles del empleado
        unavailable_days  = df_workers.loc[df_workers["Nombre"] == worker, ["Incapacidad", "Vacaciones", "Descanso", ]].values[0]
        unavailable_days  = set(sum(unavailable_days , []))

        if shift_day in unavailable_days :
            # Marcamos el turno como no asignable a este empleado
            return model.x[shift, worker] == 0
        return Constraint.Skip

    def one_shift_per_day_rule(model, worker, day):
        # Restricción: Un empleado no puede tener más de un turno por día
        shifts_day = [shift for shift in turnos if df_shifts.loc[shift, "Día del mes"] == day]
        return sum(model.x[shift, worker] for shift in shifts_day) <= 1

    def monthly_hours_limit_rule(model, worker):
        # Restricción:
        # no exceder las horas mensuales
        available_hours = df_workers.loc[df_workers["Nombre"]
                                            == worker, "Cantidad de horas disponibles del mes"].values[0]
        return sum(model.x[turno, worker] * df_shifts.loc[turno, "Horas turno"] for turno in turnos) <= available_hours


    # Definimos las restricciones
    model.cubrir_turnos = Constraint(turnos, rule=cover_shifts_rule)
    model.tienda_trabajo = Constraint(turnos, workers, rule=store_work_rule)
    model.disponibilidad = Constraint(turnos, workers, rule=availability_rule) #Dias no disponibles para un empleado
    model.un_turno_por_dia = Constraint(workers, days_in_month, rule=one_shift_per_day_rule)
    model.limite_horas = Constraint(workers, rule=monthly_hours_limit_rule)


    # Funciones de calculo de expresiones
    def calcular_horas_necesarias_tienda(tienda):
        return sum(
            df_shifts.loc[t, "Horas turno"] * df_shifts.loc[t, "Cantidad personas (con este turno)"]
            for t in turnos if df_shifts.loc[t, "Nombre Tienda"] == tienda
        )

    def calculate_available_hours_store_employees(shop):
        empleados_tienda = set()
        for t in turnos:
            if df_shifts.loc[t, "Nombre Tienda"] == shop:
                for e in workers:
                    if model.x[t, e].value == 1:
                        empleados_tienda.add(e)
        return sum(
            df_workers.loc[df_workers["Nombre"] == e, "Cantidad de horas disponibles del mes"].values[0]
            for e in empleados_tienda
        )

    # Definimos la función objetivo
    sum_differences = sum(
        (calculate_available_hours_store_employees(shop) - calcular_horas_necesarias_tienda(shop))
        for shop in tiendas
    )

    model.obj = Objective(
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
            if df_shifts.loc[t, "Nombre Tienda"] == tienda:
                for e in workers:
                    if model.x[t, e].value == 1:
                        empleados_tienda.add(e)
        
        # Calcular horas disponibles
        horas_disponibles = sum(
            df_workers.loc[df_workers["Nombre"] == e, "Cantidad de horas disponibles del mes"].values[0]
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
        for e in workers:
            if model.x[t, e].value == 1:
                asignaciones.append({
                    "Nombre": e,
                    "Nombre Tienda": df_shifts.loc[t, "Nombre Tienda"],
                    "Días": df_shifts.loc[t, "Días"],
                    "Hora Inicio punto": df_shifts.loc[t, "Hora Inicio punto"],
                    "Hora Final punto": df_shifts.loc[t, "Hora Final punto"],
                    "Horas Apertura por día": df_shifts.loc[t, "Horas Apertura por día"],
                    "Inicio turno": df_shifts.loc[t, "Inicio turno"],
                    "Fin turno": df_shifts.loc[t, "Fin turno"],
                    "Horas turno": df_shifts.loc[t, "Horas turno"],
                    "Día del mes": df_shifts.loc[t, "Día del mes"],
                })

    # Guardar el resultado
    df_asignaciones = pd.DataFrame(asignaciones)
    df_asignaciones.to_csv("../outputs/asignacion_turnos.csv", index=False)

    return df_asignaciones