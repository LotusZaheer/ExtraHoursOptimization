import pandas as pd
import json
import calendar
import ast

# Cargar datos
def load_data():
    turnos = pd.read_csv('../outputs/asignacion_turnos.csv')
    productividad = pd.read_csv('../outputs/horas_por_trabajador.csv')
    return turnos, productividad

turnos_data, productividad_data = load_data()

# Asignar colores a tiendas y horarios
tiendas_unicas = set()
for tiendas in productividad_data['Lista de tiendas asignadas']:
    tiendas = ast.literal_eval(tiendas)  # Convierte la cadena en una lista real
    tiendas_unicas.update(tiendas)
colores_tiendas = {tienda: f'#{hash(tienda) % 0xFFFFFF:06x}' for tienda in tiendas_unicas}

horarios_unicos = turnos_data[['Inicio turno', 'Fin turno']].drop_duplicates()
horarios_unicos['Horario'] = horarios_unicos.apply(lambda row: f"{row['Inicio turno']} - {row['Fin turno']}", axis=1)
colores_horarios = {horario: f'#{hash(horario) % 0xFFFFFF:06x}' for horario in horarios_unicos['Horario'].unique()}

# Convertir datos a JSON
turnos_json = turnos_data.to_dict(orient='records')
productividad_json = productividad_data.set_index('Nombre').to_dict(orient='index')

# Obtener el primer día de enero de 2025
first_weekday, _ = calendar.monthrange(2025, 1)
weekdays = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

# Generar HTML
html = f"""<!DOCTYPE html>
<html lang='es'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>Calendario de Turnos</title>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .container {{ width: 90%; max-width: 800px; margin: auto; }}
        .summary {{ margin-bottom: 20px; padding: 10px; border: 1px solid #ddd; }}
        .calendar-container {{ width: 100%; }}
        .weekdays, .calendar {{ display: grid; grid-template-columns: repeat(7, 1fr); text-align: center; }}
        .weekdays div {{ font-weight: bold; }}
        .day {{ border: 1px solid #ccc; padding: 10px; min-height: 70px; position: relative; }}
        .day-number {{ position: absolute; top: 5px; right: 5px; font-size: 12px; font-weight: bold; }}
        .legend {{ display: flex; flex-wrap: wrap; margin-top: 20px; }}
        .legend-item {{ margin-right: 10px; padding: 5px 10px; border-radius: 5px; font-size: 14px; }}
    </style>
</head>
<body>
    <div class='container'>
        <h1>Calendario de Turnos</h1>
        <div class='summary' id='summary'></div>
        
        <label for='empleado'>Empleado:</label>
        <select id='empleado'>
            <option value=''>Seleccione un empleado</option>"""
for empleado in productividad_data['Nombre']:
    html += f"<option value='{empleado}'>{empleado}</option>"
html += """
        </select>

        <div class='calendar-container'>
            <div class='weekdays'>"""
for day in weekdays:
    html += f"<div>{day}</div>"
html += """
            </div>
            <div class='calendar' id='calendar'>"""

for _ in range(first_weekday):
    html += "<div class='day'></div>"

for day in range(1, 32):
    print(f"Generando día {day}...")
    html += f"""
        <div class='day' data-day='{day}'>
            <div class='day-number'>{day}</div>
        </div>"""
html += """
            </div>
        </div>

        <div class='legend'>
            <h3>Colores por tienda:</h3>"""
for tienda, color in colores_tiendas.items():
    html += f"<div class='legend-item' style='background: {color};'>{tienda}</div>"

html += """
            <h3>Colores por horario:</h3>"""
for horario, color in colores_horarios.items():
    html += f"<div class='legend-item' style='background: {color};'>{horario}</div>"

html += """
        </div>
    </div>

    <script>
        var turnos = """ + json.dumps(turnos_json) + """;
        var productividad = """ + json.dumps(productividad_json) + """;

        document.getElementById('empleado').addEventListener('change', function() {
            var empleado = this.value;
            var calendarDays = document.querySelectorAll('.day');
            calendarDays.forEach(day => day.innerHTML = `<div class='day-number'>${day.getAttribute('data-day')}</div>`);

            if (empleado) {
                var data = productividad[empleado];
                var summaryHTML = `<h2>Resumen de ${empleado}</h2>`;
                summaryHTML += `<p><strong>Productividad:</strong> ${data['Productividad (%)'].toFixed(2)}%</p>`;
                summaryHTML += `<p><strong>Días de descanso:</strong> ${data['Días de descanso']} (${data['Lista de días de descanso']})</p>`;
                summaryHTML += `<p><strong>Días de vacaciones:</strong> ${data['Días de vacaciones']} (${data['Lista de días de vacaciones']})</p>`;
                summaryHTML += `<p><strong>Días de incapacidad:</strong> ${data['Días de incapacidad']} (${data['Lista de días de incapacidad']})</p>`;
                document.getElementById('summary').innerHTML = summaryHTML;
            }

            var turnosEmpleado = turnos.filter(t => t['Nombre'] === empleado);
            turnosEmpleado.forEach(turno => {
                var dayElement = document.querySelector(`.day[data-day='${turno['Día del mes']}']`);
                if (dayElement) {
                    var tiendaColor = '""" + json.dumps(colores_tiendas) + """'[turno['Nombre Tienda']];
                    var horario = turno['Inicio turno'] + ' - ' + turno['Fin turno'];
                    var horarioColor = '""" + json.dumps(colores_horarios) + """'[horario];
                    
                    dayElement.innerHTML += `
                        <br>
                        <span style="background: ${tiendaColor}; padding: 2px 5px; border-radius: 3px;">${turno['Nombre Tienda']}</span>
                        <span style="background: ${horarioColor}; padding: 2px 5px; border-radius: 3px;">${horario}</span>
                    `;
                }
            });
        });
    </script>
</body>
</html>"""

with open('calendario.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Archivo 'calendario.html' generado con éxito.")




