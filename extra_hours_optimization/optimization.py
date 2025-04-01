import pandas as pd
from pyomo.environ import (Constraint, ConcreteModel, Var, 
                           Binary, NonNegativeReals, 
                           minimize, maximize, 
                           Objective, SolverFactory)


def optimize_shifts(df_shifts, df_workers):

    ################ Variables auxiliares ################ 
    shifts = df_shifts.index.tolist()
    workers = df_workers["Nombre"].tolist()
    days_in_month = df_shifts["Día del mes"].unique()
    shops = df_shifts["Nombre Tienda"].unique()

    ################ Crear el modelo de optimización ################
    model = ConcreteModel()

    ################ Variables de decisión ################ 
    model.x = Var(shifts, workers, domain=Binary)


    ################ Funciones de restricción ################ 
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
        shifts_day = [shift for shift in shifts if df_shifts.loc[shift, "Día del mes"] == day]
        return sum(model.x[shift, worker] for shift in shifts_day) <= 1

    def monthly_hours_limit_rule(model, worker):
        # Restricción:
        # no exceder las horas mensuales
        available_hours = df_workers.loc[df_workers["Nombre"]
                                            == worker, "Cantidad de horas disponibles del mes"].values[0]
        return sum(model.x[turno, worker] * df_shifts.loc[turno, "Horas turno"] for turno in shifts) <= available_hours



    ################# Definimos las restricciones ################ 
    model.cover_shifts = Constraint(shifts, rule=cover_shifts_rule)
    model.store_work = Constraint(shifts, workers, rule=store_work_rule)
    model.availability = Constraint(shifts, workers, rule=availability_rule)  # Unavailable days for a worker
    model.one_shift_per_day = Constraint(workers, days_in_month, rule=one_shift_per_day_rule)
    model.monthly_hours_limit = Constraint(workers, rule=monthly_hours_limit_rule)


    ################ Funciones de calculo de expresiones ################ 
    def calculate_required_hours_store(store):
        return sum(
            df_shifts.loc[t, "Horas turno"] * df_shifts.loc[t, "Cantidad personas (con este turno)"]
            for t in shifts if df_shifts.loc[t, "Nombre Tienda"] == store
        )


    def calculate_available_hours_store_employees(shop):
        empleados_tienda = set()
        for t in shifts:
            if df_shifts.loc[t, "Nombre Tienda"] == shop:
                for e in workers:
                    if model.x[t, e].value == 1:
                        empleados_tienda.add(e)
        return sum(
            df_workers.loc[df_workers["Nombre"] == e, "Cantidad de horas disponibles del mes"].values[0]
            for e in empleados_tienda
        )

    ################ Definimos la función objetivo ################ 
    sum_differences = sum(
        (calculate_available_hours_store_employees(shop) - calculate_required_hours_store(shop))
        for shop in shops
    )

    model.obj = Objective(
        expr=abs(sum_differences),
        sense=minimize
    )

    ################ Ejecutar el modelo ################
    solver = SolverFactory("glpk")
    solver.solve(model)


    ################ Revisión de resultados ################
    print("\nInformación por tienda:")
    suma_total_horas_necesarias = 0
    suma_total_horas_disponibles = 0
    
    for tienda in shops:

        horas_necesarias = calculate_required_hours_store(tienda)
        suma_total_horas_necesarias += horas_necesarias
        

        empleados_tienda = set()
        for t in shifts:
            if df_shifts.loc[t, "Nombre Tienda"] == tienda:
                for e in workers:
                    if model.x[t, e].value == 1:
                        empleados_tienda.add(e)
        

        horas_disponibles = sum(
            df_workers.loc[df_workers["Nombre"] == e, "Cantidad de horas disponibles del mes"].values[0]
            for e in empleados_tienda
        )
        suma_total_horas_disponibles += horas_disponibles
        

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
    for t in shifts:
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

    df_assignments = pd.DataFrame(asignaciones)
    df_assignments.to_csv("../outputs/asignacion_turnos.csv", index=False)

    return df_assignments