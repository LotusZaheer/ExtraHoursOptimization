import calendar
import pandas as pd
import math
import ast

def calculate_monthly_hours(month: int, year: int, weekly_hours: int):
    days_in_month = calendar.monthrange(year, month)[1]
    weeks_in_month = round(days_in_month / 7, 2)
    monthly_hours = round(weekly_hours * weeks_in_month)
    return monthly_hours

def process_worker_data(init_data, df):

    # Calcular horas mensuales
    month, year, weekly_hours = init_data['month'], init_data['year'], init_data['weekly_hours']
    monthly_hours = calculate_monthly_hours(month, year, weekly_hours)
    
    # Factor de horas por día
    factor = 7.66  # promedio de horas por día (horas semanales / días laborales por semana)

    # Procesar listas de días
    for col in ['incapacidades', 'vacaciones', 'descanso']:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.strip().startswith('[') else [])
            df[f'Cantidad Días {col.capitalize()}'] = df[col].apply(len)
        else:
            df[col] = [[] for _ in range(len(df))]
            df[f'Cantidad Días {col.capitalize()}'] = 0


    # Calcular horas disponibles
    df['Horas perdidas por incapacidad'] = df['Cantidad Días Incapacidades'] * factor
    df['Horas perdidas por vacaciones'] = df['Cantidad Días Vacaciones'] * factor
    df['Cantidad de horas disponibles del mes'] = df.apply(
        lambda row: math.floor(max(0, monthly_hours - row['Horas perdidas por incapacidad'] - row['Horas perdidas por vacaciones'])),
        axis=1
    )
    
    # Calcular horas extra disponibles
    df['Horas extra disponibles'] = df['Cantidad de horas disponibles del mes'].apply(
        lambda x: 10 if x > 200 else 0
    )
    
    # Renombrar columnas para mantener consistencia
    df = df.rename(columns={
        'nombre': 'Nombre',
        'punto': 'Encargada punto',
        'incapacidades': 'Incapacidad',
        'vacaciones': 'Vacaciones',
        'descanso': 'Descanso'
    })
    
    # Seleccionar y ordenar columnas
    columns_order = [
        "Nombre", "Encargada punto", "Descanso", "Cantidad Días Descanso", 
        "Incapacidad", "Cantidad Días Incapacidades", "Vacaciones", "Cantidad Días Vacaciones", 
        "Cantidad de horas disponibles del mes", "Horas extra disponibles"
    ]
    df = df[columns_order]
    
    # Guardar el resultado
    df.to_csv("../intermediate_data/workers.csv", index=False, encoding='utf-8')
    print("CSV generado: trabajadores.csv")