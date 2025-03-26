import calendar
import holidays

dias_semana = {"LU": 0, "MA": 1, "MI": 2,
               "JU": 3, "VI": 4, "SA": 5, "DO": 6, "FE": 7}


def obtener_dias_mes(dia_semana, anio=2025, mes=1, pais="CO"):
    num_dia = dias_semana.get(dia_semana)
    if num_dia is None:
        return ""

    # Obtener los festivos del país
    festivos = holidays.country_holidays(pais, years=anio)

    ultimo_dia = calendar.monthrange(anio, mes)[1]

    if dia_semana == "FE":
        # Devolver solo los días festivos del mes
        return ",".join(
            str(dia) for dia in range(1, ultimo_dia + 1)
            if f"{anio}-{mes:02d}-{dia:02d}" in festivos
        )
    else:
        # Devolver los días del mes que sean el día de la semana indicado y no sean festivos
        return ",".join(
            str(dia) for dia in range(1, ultimo_dia + 1)
            if calendar.weekday(anio, mes, dia) == num_dia and f"{anio}-{mes:02d}-{dia:02d}" not in festivos
        )


# Ejemplo de uso
print(obtener_dias_mes("LU", 2025, 3))  # Lunes de marzo 2025 (sin festivos)
print(obtener_dias_mes("FE", 2025, 3))  # Festivos de marzo 2025


def obtener_dias_mes(dia_semana, anio=2025, mes=1):
    num_dia = dias_semana.get(dia_semana)
    if num_dia is None:
        return ""
    ultimo_dia = calendar.monthrange(anio, mes)[1]
    return ",".join(str(dia) for dia in range(1, ultimo_dia + 1) if calendar.weekday(anio, mes, dia) == num_dia)


# Ejemplo de uso
print(obtener_dias_mes("LU", 2025, 3))  # Lunes de marzo 2025 (sin festivos)
print(obtener_dias_mes("FE", 2025, 3))  # Festivos de marzo 2025
