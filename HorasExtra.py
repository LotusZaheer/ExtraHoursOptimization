import pandas as pd
import calendar
from pyomo.environ import *
import holidays

df = pd.read_csv("data.csv")


def expand_days(row):
    days = row["Días"].split(", ")
    expanded_rows = []
    for day in days:
        new_row = row.copy()
        new_row["Días"] = day
        expanded_rows.append(new_row)
    return expanded_rows


df_turnos = pd.DataFrame(
    [row for rows in df.apply(expand_days, axis=1) for row in rows])
df_turnos.reset_index(drop=True, inplace=True)

dias_semana = {"LU": 0, "MA": 1, "MI": 2,
               "JU": 3, "VI": 4, "SA": 5, "DO": 6, "FE": 7}


def obtener_dias_mes(dia_semana, anio=2025, mes=1, pais="CO"):
    num_dia = dias_semana.get(dia_semana)
    if num_dia is None:
        return ""

    festivos = holidays.country_holidays(pais, years=anio)

    ultimo_dia = calendar.monthrange(anio, mes)[1]

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


df_turnos["Días del mes"] = df_turnos["Días"].apply(obtener_dias_mes)

print(df_turnos.head())

df_turnos = df_turnos[df_turnos["Días del mes"].notna() & (
    df_turnos["Días del mes"] != "")]

df_turnos_expandidos = df_turnos.assign(
    **{"Día del mes": df_turnos["Días del mes"].str.split(",")}).explode("Día del mes")

df_turnos_expandidos = df_turnos_expandidos.dropna(subset=["Día del mes"])

df_turnos_expandidos["Día del mes"] = pd.to_numeric(
    df_turnos_expandidos["Día del mes"], errors="coerce").dropna().astype(int)

df_turnos_expandidos = df_turnos_expandidos.drop(columns=["Días del mes"])

df_turnos_expandidos.to_csv("turnos_expandidos.csv", index=False)


###########################################################################

###########################################################################

df_turnos = pd.read_csv("turnos_expandidos.csv")
df_empleados = pd.read_csv("trabajadores.csv")

df_empleados["Incapacidad"] = df_empleados["Incapacidad"].fillna(
    "").apply(lambda x: list(map(int, str(x).split(","))) if x else [])
df_empleados["Vacaciones"] = df_empleados["Vacaciones"].fillna(
    "").apply(lambda x: list(map(int, str(x).split(","))) if x else [])


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
    dias_no_disponibles = df_empleados.loc[df_empleados["Nombre"] == e, [
        "Incapacidad", "Vacaciones"]].sum()
    if dia_turno in dias_no_disponibles:
        return model.x[t, e] == 0
    return Constraint.Skip


model.disponibilidad = Constraint(turnos, empleados, rule=disponibilidad_rule)

# Restricción:
# no exceder las horas mensuales


def limite_horas_rule(model, e):
    horas_disponibles = df_empleados.loc[df_empleados["Nombre"]
                                         == e, "Cantidad de horas disponibles del mes"].values[0]
    return sum(model.x[t, e] * df_turnos.loc[t, "Horas turno"] for t in turnos) <= horas_disponibles


model.limite_horas = Constraint(empleados, rule=limite_horas_rule)

# Función objetivo: minimizar la cantidad de turnos sin asignar
model.obj = Objective(
    expr=sum(model.x[t, e] for t in turnos for e in empleados), sense=maximize)


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
                "Cantidad de días": df_turnos.loc[t, "Cantidad de días"],
                "Hora Inicio punto": df_turnos.loc[t, "Hora Inicio punto"],
                "Hora Final punto": df_turnos.loc[t, "Hora Final punto"],
                "Horas Apertura por día": df_turnos.loc[t, "Horas Apertura por día"],
                "Inicio turno": df_turnos.loc[t, "Inicio turno"],
                "Fin turno": df_turnos.loc[t, "Fin turno"],
                "Horas turno": df_turnos.loc[t, "Horas turno"],
                "Cantidad personas (con este turno)": df_turnos.loc[t, "Cantidad personas (con este turno)"],
                "Horas a trabajar por semana": df_turnos.loc[t, "Horas a trabajar por semana"],
                "Día del mes": df_turnos.loc[t, "Día del mes"]
            })

# Guardar el resultado
df_asignaciones = pd.DataFrame(asignaciones)
df_asignaciones.to_csv("asignacion_turnos.csv", index=False)


# Calcular horas asignadas por trabajador
df_horas_por_trabajador = df_asignaciones.groupby(
    "Nombre")["Horas turno"].sum().reset_index()
df_horas_por_trabajador.to_csv("horas_por_trabajador.csv", index=False)
print("Horas asignadas por trabajador")
print(df_horas_por_trabajador.head())

# Calcular horas asignadas por tienda
df_horas_por_tienda = df_asignaciones.groupby(
    "Nombre Tienda")["Horas turno"].sum().reset_index()
df_horas_por_tienda.to_csv("horas_por_tienda.csv", index=False)
print("Horas asignadas por tienda")
print(df_horas_por_tienda.head())
