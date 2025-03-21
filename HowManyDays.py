import calendar


def contar_dias(dias, anio=2025, mes=1):
    dias_semana = {"LU": 0, "MA": 1, "MI": 2,
                   "JU": 3, "VI": 4, "SA": 5, "DO": 6}
    dias_indices = [dias_semana[d] for d in dias]
    return sum(1 for dia in range(1, calendar.monthrange(anio, mes)[1] + 1) if calendar.weekday(anio, mes, dia) in dias_indices)


dias_a_contar = ["LU", "MA", "MI", "JU"]
print(contar_dias(dias_a_contar, 2025, 1))  # Enero 2025
