from pyomo.environ import *
import pandas as pd

# Cargar datos
data = pd.read_csv("data.csv")
restrictions = pd.read_csv("restrictions.csv")

# Crear modelo
model = ConcreteModel()

# Conjuntos
empleados = list(restrictions["Nombre"].unique())
turnos = list(data.index)
semanas = list(range(4))  # Considerando 4 semanas en un mes

model.E = Set(initialize=empleados)
model.T = Set(initialize=turnos)
model.S = Set(initialize=semanas)

# Parámetros
horas_empleado = {row["Nombre"]: row["Horas_Disponibles"]
                  for _, row in restrictions.iterrows()}
horas_turno = {idx: row["Horas turno"] for idx, row in data.iterrows()}
personas_necesarias = {
    idx: row["Cantidad personas (con este turno)"] for idx, row in data.iterrows()}

# Variables
model.x = Var(model.E, model.T, model.S, domain=Binary)

# Restricción: No exceder horas del empleado
model.horas_max = ConstraintList()
for e in empleados:
    for s in semanas:
        model.horas_max.add(
            sum(model.x[e, t, s] * horas_turno[t]
                for t in turnos if (e, t, s) in model.x) <= horas_empleado[e] / 4
        )

# Restricción: Cubrir la cantidad de personas necesarias por turno
model.cobertura_turnos = ConstraintList()
for t in turnos:
    for s in semanas:
        model.cobertura_turnos.add(
            sum(model.x[e, t, s] for e in empleados if (
                e, t, s) in model.x) == personas_necesarias[t]
        )

# Función objetivo (Distribuir equitativamente los turnos)
model.obj = Objective(
    expr=sum(model.x[e, t, s]
             for e in empleados for t in turnos for s in semanas),
    sense=maximize
)

# Resolver
solver = SolverFactory("glpk")
solver.solve(model, tee=True)

# Generar datasets de asignación
asignaciones = []
horas_empleado_total = {e: 0 for e in empleados}

tiendas = data[["Nombre Tienda"]].drop_duplicates()["Nombre Tienda"].tolist()
horas_tienda = {t: 0 for t in tiendas}

tienda_asignaciones = {t: [] for t in tiendas}

for e in empleados:
    for s in semanas:
        for t in turnos:
            if model.x[e, t, s].value == 1:
                tienda = data.loc[t, "Nombre Tienda"]
                horas = horas_turno[t]
                asignaciones.append([e, tienda, s, horas])
                horas_empleado_total[e] += horas
                horas_tienda[tienda] += horas
                tienda_asignaciones[tienda].append(e)

# Guardar datasets
asignaciones_df = pd.DataFrame(
    asignaciones, columns=["Empleado", "Tienda", "Semana", "Horas Trabajadas"])
asignaciones_df.to_csv("asignaciones.csv", index=False)

horas_empleado_df = pd.DataFrame(list(horas_empleado_total.items()), columns=[
                                 "Empleado", "Horas Totales"])
horas_empleado_df.to_csv("horas_empleados.csv", index=False)

horas_tienda_df = pd.DataFrame([(t, len(set(tienda_asignaciones[t])), horas_tienda[t])
                               for t in tiendas], columns=["Tienda", "Empleados Asignados", "Horas Totales"])
horas_tienda_df.to_csv("horas_tiendas.csv", index=False)
