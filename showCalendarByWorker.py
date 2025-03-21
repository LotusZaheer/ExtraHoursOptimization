# asignacion_turnos
import pandas as pd
import json
import calendar


def load_data():
    df = pd.read_csv('outputs/asignacion_turnos.csv')
    return df


data = load_data()


def generate_html(data):
    empleados = data['Nombre'].unique()
    data_json = json.dumps(data.to_dict(orient='records'))

    # Obtener el primer día de enero de 2025
    first_weekday, _ = calendar.monthrange(2025, 1)
    weekdays = ['Lunes', 'Martes', 'Miércoles',
                'Jueves', 'Viernes', 'Sábado', 'Domingo']

    html = f"""<!DOCTYPE html>
    <html lang='es'>
    <head>
        <meta charset='UTF-8'>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <title>Calendario de Turnos</title>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .calendar-container {{ width: 100%; max-width: 800px; margin: auto; }}
            .weekdays {{ display: grid; grid-template-columns: repeat(7, 1fr); text-align: center; font-weight: bold; margin-bottom: 10px; }}
            .calendar {{ display: grid; grid-template-columns: repeat(7, 1fr); gap: 10px; }}
            .day {{ border: 1px solid #ccc; padding: 10px; position: relative; min-height: 50px; }}
            .day-number {{ position: absolute; top: 5px; right: 5px; font-size: 12px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>Calendario de Turnos</h1>
        <label for='empleado'>Empleado:</label>
        <select id='empleado'>
            <option value=''>Seleccione un empleado</option>
    """
    for empleado in empleados:
        html += f"<option value='{empleado}'>{empleado}</option>"

    html += """
        </select>
        <div class='calendar-container'>
            <div class='weekdays'>
    """
    for day in weekdays:
        html += f"<div>{day}</div>"

    html += """
            </div>
            <div class='calendar' id='calendar'>
    """

    for _ in range(first_weekday):
        html += "<div class='day'></div>"

    for day in range(1, 32):
        html += f"""
            <div class='day' data-day='{day}'>
                <div class='day-number'>{day}</div>
            </div>
        """

    html += f"""
            </div>
        </div>
        <script>
            var data = {data_json};
            document.getElementById('empleado').addEventListener('change', function() {{
                var empleado = this.value;
                var calendarDays = document.querySelectorAll('.day');
                calendarDays.forEach(day => day.innerHTML = `<div class='day-number'>${{day.getAttribute('data-day')}}</div>`);
                
                var turnos = data.filter(t => t['Nombre'] === empleado);
                turnos.forEach(turno => {{
                    var dayElement = document.querySelector(`.day[data-day='${{turno['Día del mes']}}']`);
                    if (dayElement) {{
                        dayElement.innerHTML += `<br>${{turno['Nombre Tienda']}} (${{turno['Inicio turno']}} - ${{turno['Fin turno']}})`;
                    }}
                }});
            }});
        </script>
    </body>
    </html>"""

    with open('calendario.html', 'w', encoding='utf-8') as f:
        f.write(html)


generate_html(data)
