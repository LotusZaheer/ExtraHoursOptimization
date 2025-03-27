import calendar
import pandas as pd

def calcular_horas_mes(mes: int, anio: int, horas_semana: int):
    dias_mes = calendar.monthrange(anio, mes)[1]
    semanas_mes = round(dias_mes / 7, 2)
    horas_mes = round(horas_semana * semanas_mes)
    return dias_mes, semanas_mes, horas_mes

def procesar_empleados(empleados, horas_mes):
    factor = 7.66
    data = []
    
    for empleado in empleados:
        dias_incapacidad = empleado.get('incapacidades', [])
        dias_vacaciones = empleado.get('vacaciones', [])
        dias_descanso = empleado.get('descanso', [])
        
        horas_perdidas_incapacidad = len(dias_incapacidad) * factor
        horas_perdidas_vacaciones = len(dias_vacaciones) * factor

        print('dias_incapacidad', len(dias_incapacidad), 'dias_vacaciones', len(dias_vacaciones))

        horas_disponibles = round(max(0, horas_mes - horas_perdidas_incapacidad - horas_perdidas_vacaciones))

        horas_extra = 10 if horas_disponibles > 200 else 0  # Ajuste basado en la tabla de referencia
        
        data.append([
            empleado['nombre'],
            empleado.get('punto', ''),
            ",".join(map(str, dias_descanso)) if dias_descanso else "",
            len(dias_descanso),
            ",".join(map(str, dias_incapacidad)) if dias_incapacidad else "",
            len(dias_incapacidad),
            ",".join(map(str, dias_vacaciones)) if dias_vacaciones else "",
            len(dias_vacaciones),
            horas_disponibles,
            horas_extra
        ])
    
    df = pd.DataFrame(data, columns=[
        "Nombre", "Encargada punto", "Descanso", "Cantidad Días Descanso", 
        "Incapacidad", "Cantidad Días Incapacidad", "Vacaciones", "Cantidad de días Vacaciones", 
        "Cantidad de horas disponibles del mes", "Horas extra disponibles"
    ])
    
    df.to_csv("../inputs/empleados_horas.csv", index=False, encoding='utf-8')
    print("CSV generado: empleados_horas.csv")

# Parámetros
mes, anio, horas_semana = 1, 2025, 46
dias_mes, semanas_mes, horas_mes = calcular_horas_mes(mes, anio, horas_semana)

empleados = [
    {"nombre": "E_AG", "punto": "T_MB", "vacaciones":[], "incapacidades": [], "vacaciones": []},
    {"nombre": "E_CG", "punto": "", "vacaciones":[], "incapacidades": [], "vacaciones": []},
    {"nombre": "E_YS", "punto": "T_EC", "vacaciones":[], "incapacidades": [], "vacaciones": [2,3,4,7,8,9,10,11,13,14,15,16,17,18,20]},
    {"nombre": "E_ZC", "punto": "", "vacaciones":[], "incapacidades": [], "vacaciones": []},
    {"nombre": "E_NJ", "punto": "", "vacaciones":[], "incapacidades": [], "vacaciones": []},
    {"nombre": "E_LV", "punto": "T_CT", "vacaciones":[], "incapacidades": [], "vacaciones": [25,26]},
    {"nombre": "E_LR", "punto": "", "vacaciones":[], "incapacidades": [], "vacaciones": []},
    {"nombre": "E_JM", "punto": "", "vacaciones":[], "incapacidades": [], "vacaciones": []},
    {"nombre": "E_AM", "punto": "", "vacaciones":[], "incapacidades": [], "vacaciones": []},
    {"nombre": "E_NB", "punto": "", "vacaciones":[], "incapacidades": [7,8,9,10], "vacaciones": []},
    {"nombre": "E_JR", "punto": "", "vacaciones":[], "incapacidades": [], "vacaciones": []},
    {"nombre": "E_AQ", "punto": "", "vacaciones":[], "incapacidades": [], "vacaciones": []},
    {"nombre": "E_AD", "punto": "", "vacaciones":[], "incapacidades": [], "vacaciones": []}
]

procesar_empleados(empleados, horas_mes)