import pandas as pd

def added_metric_to_shifts(df_shifts):

    def process_row(row):
        # Convertir la cadena de días a lista
        days = [d.strip() for d in row["Días"].split(",")]
        
        # Calcular horas de apertura y turno
        hours_open = row["Hora Final punto"] - row["Hora Inicio punto"]
        shift_hours = row["Fin turno"] - row["Inicio turno"]
        weekly_hours = shift_hours * len(days) * row["Cantidad personas (con este turno)"]
        
        return {
            "Nombre Tienda": row["Nombre Tienda"],
            "Días": row["Días"],
            "Cantidad de días": len(days),
            "Hora Inicio punto": row["Hora Inicio punto"],
            "Hora Final punto": row["Hora Final punto"],
            "Horas Apertura por día": hours_open,
            "Inicio turno": row["Inicio turno"],
            "Fin turno": row["Fin turno"],
            "Horas turno": shift_hours,
            "Cantidad personas (con este turno)": row["Cantidad personas (con este turno)"],
            "Horas a trabajar por semana": weekly_hours,
            "Horas extra posibles": row["Horas extra posibles"]
        }

    # Aplicar la función process_row a cada fila
    rows = df_shifts.apply(process_row, axis=1).tolist()

    # Crear DataFrame y guardar a CSV
    df = pd.DataFrame(rows)
    df.to_csv("../intermediate_data/expanded_shifts.csv", index=False, encoding='utf-8')
    print("Archivo de prueba generado: data.csv")
