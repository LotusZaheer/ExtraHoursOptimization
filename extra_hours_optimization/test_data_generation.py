import pandas as pd
from config import get_config

def generate_test_data():
    _, _, stores_data = get_config()
    
    # Lista para almacenar todas las filas
    rows = []

    for store_data in stores_data:
        store = store_data["store"]
        
        # Procesar horario regular
        opening_hours = store_data["opening_hours"]
        hours_open = opening_hours["end"] - opening_hours["start"]
        
        for shift in store_data["shifts"]:
            shift_hours = shift["end"] - shift["start"]
            weekly_hours = shift_hours * len(opening_hours["days"])
            
            rows.append({
                "Nombre Tienda": store,
                "Días": ", ".join(opening_hours["days"]),
                "Cantidad de días": len(opening_hours["days"]),
                "Hora Inicio punto": opening_hours["start"],
                "Hora Final punto": opening_hours["end"],
                "Horas Apertura por día": hours_open,
                "Inicio turno": shift["start"],
                "Fin turno": shift["end"],
                "Horas turno": shift_hours,
                "Cantidad personas (con este turno)": shift["people"],
                "Horas a trabajar por semana": weekly_hours,
                "Horas extra posibles": 0
            })

        # Procesar domingo si existe
        if "sunday" in store_data:
            sunday_data = store_data["sunday"]
            hours_open = sunday_data["opening_hours"]["end"] - sunday_data["opening_hours"]["start"]
            
            for shift in sunday_data["shifts"]:
                shift_hours = shift["end"] - shift["start"]
                weekly_hours = shift_hours
                
                rows.append({
                    "Nombre Tienda": store,
                    "Días": ", ".join(sunday_data["opening_hours"]["days"]),
                    "Cantidad de días": len(sunday_data["opening_hours"]["days"]),
                    "Hora Inicio punto": sunday_data["opening_hours"]["start"],
                    "Hora Final punto": sunday_data["opening_hours"]["end"],
                    "Horas Apertura por día": hours_open,
                    "Inicio turno": shift["start"],
                    "Fin turno": shift["end"],
                    "Horas turno": shift_hours,
                    "Cantidad personas (con este turno)": shift["people"],
                    "Horas a trabajar por semana": weekly_hours,
                    "Horas extra posibles": 0
                })

        # Procesar fin de semana si existe
        if "weekend" in store_data:
            weekend_data = store_data["weekend"]
            hours_open = weekend_data["opening_hours"]["end"] - weekend_data["opening_hours"]["start"]
            
            for shift in weekend_data["shifts"]:
                shift_hours = shift["end"] - shift["start"]
                weekly_hours = shift_hours * len(weekend_data["opening_hours"]["days"])
                
                rows.append({
                    "Nombre Tienda": store,
                    "Días": ", ".join(weekend_data["opening_hours"]["days"]),
                    "Cantidad de días": len(weekend_data["opening_hours"]["days"]),
                    "Hora Inicio punto": weekend_data["opening_hours"]["start"],
                    "Hora Final punto": weekend_data["opening_hours"]["end"],
                    "Horas Apertura por día": hours_open,
                    "Inicio turno": shift["start"],
                    "Fin turno": shift["end"],
                    "Horas turno": shift_hours,
                    "Cantidad personas (con este turno)": shift["people"],
                    "Horas a trabajar por semana": weekly_hours,
                    "Horas extra posibles": 0
                })

        # Procesar días festivos si existen
        if "holiday" in store_data:
            holiday_data = store_data["holiday"]
            hours_open = holiday_data["opening_hours"]["end"] - holiday_data["opening_hours"]["start"]
            
            for shift in holiday_data["shifts"]:
                shift_hours = shift["end"] - shift["start"]
                weekly_hours = shift_hours * len(holiday_data["opening_hours"]["days"])
                
                rows.append({
                    "Nombre Tienda": store,
                    "Días": ", ".join(holiday_data["opening_hours"]["days"]),
                    "Cantidad de días": len(holiday_data["opening_hours"]["days"]),
                    "Hora Inicio punto": holiday_data["opening_hours"]["start"],
                    "Hora Final punto": holiday_data["opening_hours"]["end"],
                    "Horas Apertura por día": hours_open,
                    "Inicio turno": shift["start"],
                    "Fin turno": shift["end"],
                    "Horas turno": shift_hours,
                    "Cantidad personas (con este turno)": shift["people"],
                    "Horas a trabajar por semana": weekly_hours,
                    "Horas extra posibles": 0
                })

    # Crear DataFrame y guardar a CSV
    df = pd.DataFrame(rows)
    df.to_csv("../intermediate_data/data_.csv", index=False, encoding='utf-8')
    print("Archivo de prueba generado: data.csv")
