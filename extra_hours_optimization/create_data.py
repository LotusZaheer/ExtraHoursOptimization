import calendar
import pandas as pd
import math

def calculate_monthly_hours(month: int, year: int, weekly_hours: int):
    days_in_month = calendar.monthrange(year, month)[1]
    weeks_in_month = round(days_in_month / 7, 2)
    monthly_hours = round(weekly_hours * weeks_in_month)
    return monthly_hours

def process_employees(employees, init_data):

    month, year, weekly_hours = init_data['month'], init_data['year'], init_data['weekly_hours']

    monthly_hours = calculate_monthly_hours(month, year, weekly_hours)

    factor = 7.66  # average hours per day (weekly hours / working days per week)
    data = []
    
    for employee in employees:
        sick_days = employee.get('incapacidades', [])
        vacation_days = employee.get('vacaciones', [])
        rest_days = employee.get('descanso', [])
        
        lost_hours_sick = len(sick_days) * factor
        lost_hours_vacation = len(vacation_days) * factor

        available_hours = math.floor(max(0, monthly_hours - lost_hours_sick - lost_hours_vacation))

        extra_hours = 10 if available_hours > 200 else 0  # Adjustment based on reference table
        
        data.append([
            employee['nombre'],
            employee.get('punto', ''),
            ",".join(map(str, rest_days)) if rest_days else "",
            len(rest_days) if rest_days else 0,
            ",".join(map(str, sick_days)) if sick_days else "",
            len(sick_days) if sick_days else 0,
            ",".join(map(str, vacation_days)) if vacation_days else "",
            len(vacation_days) if vacation_days else 0,
            available_hours,
            extra_hours
        ])
    df = pd.DataFrame(data, columns=[
        "Nombre", "Encargada punto", "Descanso", "Cantidad Días Descanso", 
        "Incapacidad", "Cantidad Días Incapacidad", "Vacaciones", "Cantidad de días Vacaciones", 
        "Cantidad de horas disponibles del mes", "Horas extra disponibles"
    ])
    
    df.to_csv("../intermediate_data/trabajadores.csv", index=False, encoding='utf-8')

    print("CSV generated: empleados_horas.csv")