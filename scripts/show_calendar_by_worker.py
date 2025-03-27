import pandas as pd
import json
import calendar
import ast
import matplotlib.colors as mcolors

colores_disponibles = list(mcolors.TABLEAU_COLORS.values())

# Cargar datos
def load_data():
    turnos = pd.read_csv('../outputs/asignacion_turnos.csv')
    productividad = pd.read_csv('../outputs/horas_por_trabajador.csv')
    return turnos, productividad

turnos_data, productividad_data = load_data()

# Asignar colores a tiendas y horarios
tiendas_unicas = set()
for tiendas in productividad_data['Lista de tiendas asignadas']:
    tiendas = ast.literal_eval(tiendas) # Convertirmos el string a lista
    tiendas_unicas.update(tiendas)
colores_tiendas = {tienda: f'#{hash(tienda) % 0xFFFFFF:06x}' for tienda in tiendas_unicas}
colores_tiendas = {tienda: colores_disponibles[i % len(colores_disponibles)] for i, tienda in enumerate(tiendas_unicas)}

horarios_unicos = turnos_data[['Inicio turno', 'Fin turno']].drop_duplicates()
horarios_unicos['Horario'] = horarios_unicos.apply(lambda row: f"{row['Inicio turno']} - {row['Fin turno']}", axis=1)
colores_horarios = {horario: f'#{hash(horario) % 0xFFFFFF:06x}' for horario in horarios_unicos['Horario'].unique()}
colores_horarios = {horario: colores_disponibles[i % len(colores_disponibles)] for i, horario in enumerate(horarios_unicos['Horario'].unique())}

# Convertir datos a JSON
turnos_json = turnos_data.to_dict(orient='records')
productividad_json = productividad_data.set_index('Nombre').to_dict(orient='index')

# Obtener el primer día del mes y los días de la semana
first_weekday, _ = calendar.monthrange(2025, 1)
weekdays = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

# Colores especiales para tipos de días
colores_especiales = {
    "descanso": "rgba(206, 206, 206, 0.5)",
    "vacaciones": "rgba(0, 255, 0, 0.5)",
    "incapacidad": "rgba(255, 0, 0, 0.5)",
    "trabajados": "rgba(0, 0, 139, 0.5)"
}

html = f"""<!DOCTYPE html>
<html lang='es'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>Calendario de Turnos</title>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        h3 {{ margin: 0; padding: 6px; }}
        .container {{ width: 90%; max-width: 800px; margin: auto; }}
        .summary {{ margin-bottom: 20px; padding: 10px; border: 1px solid #ddd; }}
        .calendar-container {{ width: 100%; }}
        .weekdays, .calendar {{ display: grid; grid-template-columns: repeat(7, 1fr); text-align: center; }}
        .weekdays div {{ font-weight: bold; }}
        .day {{ border: 1px solid #ccc; padding: 10px; min-height: 70px; position: relative; }}
        .day-number {{ position: absolute; top: 5px; right: 5px; font-size: 12px; font-weight: bold; }}
        .legend {{ display: flex; flex-direction: row; margin-top: 20px; }}
        .legend-item {{ margin-right: 10px; padding: 5px 10px; border-radius: 5px; font-size: 14px; }}
        
        .descanso {{ background: {colores_especiales['descanso']}; }}
        .vacaciones {{ background: {colores_especiales['vacaciones']}; }}
        .incapacidad {{ background: {colores_especiales['incapacidad']}; }}
        .trabajado {{ background: {colores_especiales['trabajados']}; }}

        .descanso-title {{ background: {colores_especiales['descanso']}; padding: 2px 5px; border-radius: 3px; }}
        .vacaciones-title {{ background: {colores_especiales['vacaciones']}; padding: 2px 5px; border-radius: 3px; }}
        .incapacidad-title {{ background: {colores_especiales['incapacidad']}; padding: 2px 5px; border-radius: 3px; }}
        .trabajado-title {{ background: {colores_especiales['trabajados']}; padding: 2px 5px; border-radius: 3px; }}

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
            <br>
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
            calendarDays.forEach(day => {
                day.classList.remove('descanso', 'vacaciones', 'incapacidad', 'trabajado');
                day.innerHTML = `<div class='day-number'>${day.getAttribute('data-day')}</div>`;
            });

            if (empleado) {
                var data = productividad[empleado];
                var summaryHTML = `<h2>Resumen de ${empleado}</h2>`;
                summaryHTML += `<p><span class="trabajado-title"><strong>Productividad:</strong></span>${data['Productividad (%)'].toFixed(2)}%</p>`;
                summaryHTML += `<p><span ><strong>Horas trabajadas:</strong></span>${data['Horas turno']}</p>`;
                summaryHTML += `<p><span ><strong>Horas disponibles:</strong></span>${data['Cantidad de horas disponibles del mes']}</p>`;
                summaryHTML += `<p><span ><strong>Horas disponibles:</strong></span>${data['Lista de tiendas asignadas'].replace(/[\[\]'"]/g, '').split(', ')}</p>`;

                summaryHTML += `<p><span class="descanso-title"><strong>Días de descanso:</strong></span> (${data['Días de descanso']}) : 
                  ${data['Lista de días descanso'].replace(/[\[\]"]/g, '').split(', ')}</p>`;
                summaryHTML += `<p><span class="vacaciones-title"><strong>Días de vacaciones:</strong></span> (${data['Días de vacaciones']}) :
                  ${data['Lista de días vacaciones'].replace(/[\[\]"]/g, '').split(', ')}</p>`;
                summaryHTML += `<p><span class="incapacidad-title"><strong>Días de incapacidad:</strong></span> (${data['Días de incapacidad']}) :
                  ${data['Lista de días incapacidad'].replace(/[\[\]"]/g, '').split(', ')}</p>`;

                document.getElementById('summary').innerHTML = summaryHTML;


                // Aplicar colores según el tipo de día
                ['descanso', 'vacaciones', 'incapacidad'].forEach(tipo => {
                    var dias = data[`Lista de días ${tipo}`];
                    if (dias) {
                        dias = dias.replace(/[\[\]"]/g, '');
                        dias.split(', ').forEach(dia => {
                            var dayElement = document.querySelector(`.day[data-day='${dia}']`);
                            if (dayElement) {
                                dayElement.classList.add(tipo);
                            }
                        });
                    }
                });

                var turnosEmpleado = turnos.filter(t => t['Nombre'] === empleado);
                turnosEmpleado.forEach(turno => {
                    var dayElement = document.querySelector(`.day[data-day='${turno['Día del mes']}']`);
                    if (dayElement) {

                    var tiendaColor = """ + json.dumps(colores_tiendas) + """[turno['Nombre Tienda']];
                    var horario = turno['Inicio turno'] + ' - ' + turno['Fin turno'];
                    var horarioColor = """ + json.dumps(colores_horarios) + """[horario];
                    
                    dayElement.innerHTML += `
                        <br>
                        <span style="background: ${tiendaColor}; padding: 2px 5px; border-radius: 3px;">${turno['Nombre Tienda']}</span>
                        <br>
                        <span style="background: ${horarioColor}; padding: 2px 5px; border-radius: 3px;">${horario}</span>
                    `;

                        dayElement.classList.add('trabajado');
                    }
                });
            }
        });
    </script>
</body>
</html>"""

with open('../html/turnos_empleado.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Archivo 'turnos_empleado.html' generado con éxito.")
