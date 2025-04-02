import pandas as pd
from config import get_config

def generate_store_shifts():
    _, _, stores_data = get_config()
    
    # Lista para almacenar todas las filas
    rows = []

    # Lista de campos que no son secciones de horarios
    non_section_fields = ["store", "holidays_available", "maintenance_days", "opening_hours", "shifts"]

    for store_data in stores_data:
        store = store_data["store"]
        
        # Procesar horario regular
        opening_hours = store_data["opening_hours"]
        hours_open = opening_hours["end"] - opening_hours["start"]
        
        for shift in store_data["shifts"]:
            shift_hours = shift["end"] - shift["start"]
            weekly_hours = shift_hours * len(opening_hours["days"]) * shift["people"]
            
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
                "Horas extra posibles": 0,
                "Tipo de horario": "regular"
            })

        # Procesar todas las secciones especiales dinámicamente
        for section_name, section_data in store_data.items():
            # Solo procesar si no es un campo de configuración principal
            if section_name not in non_section_fields:
                hours_open = section_data["opening_hours"]["end"] - section_data["opening_hours"]["start"]
                
                for shift in section_data["shifts"]:
                    shift_hours = shift["end"] - shift["start"]
                    weekly_hours = shift_hours * len(section_data["opening_hours"]["days"]) * shift["people"]
                    
                    rows.append({
                        "Nombre Tienda": store,
                        "Días": ", ".join(section_data["opening_hours"]["days"]),
                        "Cantidad de días": len(section_data["opening_hours"]["days"]),
                        "Hora Inicio punto": section_data["opening_hours"]["start"],
                        "Hora Final punto": section_data["opening_hours"]["end"],
                        "Horas Apertura por día": hours_open,
                        "Inicio turno": shift["start"],
                        "Fin turno": shift["end"],
                        "Horas turno": shift_hours,
                        "Cantidad personas (con este turno)": shift["people"],
                        "Horas a trabajar por semana": weekly_hours,
                        "Horas extra posibles": 0,
                        "Tipo de horario": section_name
                    })

    # Crear DataFrame y guardar a CSV
    df = pd.DataFrame(rows)
    df.to_csv("../intermediate_data/data.csv", index=False, encoding='utf-8')
    print("Archivo de prueba generado: data.csv")
