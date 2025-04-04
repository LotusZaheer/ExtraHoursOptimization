# asignacion_turnos
import pandas as pd
import json
import calendar
import holidays

colores_disponibles = [
    "#FE0000", "#FED500", "#0485AD", "#18A222", "#7B00CB",
    "#FE00C6", "#0C54DF", "#087376", "#AD002F", "#BE5504",
    "#84D401", "#0A2683", "#9B8947", "#00CE94", "#ED7014",
    "#3B8761", "#D10056", "#67032F", "#EB8FE9", "#064D06"
]

def load_data():
    df = pd.read_csv('../outputs/asignacion_turnos.csv')
    horarios_tiendas = pd.read_csv('../intermediate_data/expanded_shifts.csv')
    return df, horarios_tiendas

def generate_shop_calendar(init_data):
    print("Generando calendario de turnos por tienda...")
    stores_data = init_data['stores_data']
    data, horarios_tiendas = load_data()

    # Obtener días festivos
    holidays_list = holidays.country_holidays(init_data['country'], years=init_data['year'])
    festivos = [day.day for day in holidays_list.keys() if day.month == init_data['month']]

    # Obtener días de mantenimiento por tienda
    dias_mantenimiento = {store["store"]: store["maintenance_days"] for store in stores_data}

    # Asignar colores a trabajadores y horarios
    trabajadores_unicos = data['Nombre'].unique()
    colores_trabajadores = {trabajador: colores_disponibles[i % len(colores_disponibles)] 
                           for i, trabajador in enumerate(trabajadores_unicos)}

    horarios_unicos = data[['Inicio turno', 'Fin turno']].drop_duplicates()
    horarios_unicos['Horario'] = horarios_unicos.apply(lambda row: f"{row['Inicio turno']} - {row['Fin turno']}", axis=1)
    colores_horarios = {horario: colores_disponibles[i % len(colores_disponibles)] 
                       for i, horario in enumerate(horarios_unicos['Horario'].unique())}

    # Colores para días especiales
    colores_especiales = {
        "festivo": "rgba(255, 165, 0, 0.3)",  # Naranja para festivos
        "mantenimiento": "rgba(169, 169, 169, 0.3)"  # Gris para mantenimiento
    }

    # Mapeo de días de la semana
    dias_semana = {
        "LU": "Lunes",
        "MA": "Martes",
        "MI": "Miércoles",
        "JU": "Jueves",
        "VI": "Viernes",
        "SA": "Sábado",
        "DO": "Domingo",
        "FE": "Festivo",
        "MN": "Mantenimiento"
    }

    tiendas = data['Nombre Tienda'].unique()
    data_json = json.dumps(data.to_dict(orient='records'))
    colores_trabajadores_json = json.dumps(colores_trabajadores)
    colores_horarios_json = json.dumps(colores_horarios)
    colores_especiales_json = json.dumps(colores_especiales)
    festivos_json = json.dumps(festivos)
    dias_mantenimiento_json = json.dumps(dias_mantenimiento)

    # Procesar horarios de tiendas
    horarios_tiendas_json = {}
    for tienda in tiendas:
        horarios_tienda = horarios_tiendas[horarios_tiendas['Nombre Tienda'] == tienda]
        horarios_tienda = horarios_tienda[['Días', 'Hora Inicio punto', 'Hora Final punto']]
        horarios_tienda['Días'] = horarios_tienda['Días'].apply(lambda x: x.split(', '))
        horarios_tienda = horarios_tienda.explode('Días')
        horarios_tienda['Días'] = horarios_tienda['Días'].map(dias_semana)
        horarios_tienda['Horario'] = horarios_tienda.apply(lambda x: f"{x['Hora Inicio punto']} - {x['Hora Final punto']}", axis=1)
        
        # Eliminar duplicados y agrupar por día
        horarios_tienda = horarios_tienda.drop_duplicates(subset=['Días'])
        horarios_tienda = horarios_tienda.sort_values('Días')
        horarios_tienda = horarios_tienda[['Días', 'Horario']].to_dict('records')
        horarios_tiendas_json[tienda] = horarios_tienda

    horarios_tiendas_json = json.dumps(horarios_tiendas_json)

    # Obtener el primer día de enero de 2025
    first_weekday, _ = calendar.monthrange(2025, 1)
    weekdays = ['Lunes', 'Martes', 'Miércoles',
                'Jueves', 'Viernes', 'Sábado', 'Domingo']

    html = f"""<!DOCTYPE html>
    <html lang='es'>
    <head>
        <meta charset='UTF-8'>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <title>Turnos por Tienda</title>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .calendar-container {{ width: 100%; max-width: 1200px; margin: auto; }}
            .weekdays {{ display: grid; grid-template-columns: repeat(7, 1fr); text-align: center; font-weight: bold; margin-bottom: 10px; }}
            .calendar {{ display: grid; grid-template-columns: repeat(7, 1fr); gap: 10px; }}
            .day {{ border: 1px solid #ccc; padding: 10px; position: relative; height: fit-content; }}
            .day-number {{ position: static; top: 5px; right: 5px; font-size: 12px; font-weight: bold; }}
            .turno-container {{ 
                display: flex; 
                align-items: center; 
                gap: 3px; 
                margin-bottom: 3px;
                justify-content: space-between;
                width: 100%;
                margin-top: 3px;
            }}
            .turno-trabajador {{ 
                padding: 2px 5px; 
                border-radius: 3px;
                flex: 1;
                text-align: left;
            }}
            .turno-horario {{ 
                padding: 2px 5px; 
                border-radius: 3px;
                flex: 1;
                text-align: right;
            }}
            .turno-info {{ 
                white-space: nowrap; 
                overflow: hidden; 
                text-overflow: ellipsis;
                max-width: 45%;
            }}
            .legend {{ display: flex; flex-direction: row; flex-wrap: wrap; margin-top: 20px; gap: 10px; }}
            .legend-item {{ padding: 5px 10px; border-radius: 5px; font-size: 14px; white-space: nowrap; }}
            .dia-especial {{ position: absolute; top: 5px; left: 5px; font-size: 12px; font-weight: bold; }}
            .horarios-tienda {{ 
                margin: 20px 0;
                padding: 15px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9f9f9;
            }}
            .horarios-tienda h3 {{ margin-top: 0; }}
            .horarios-grid {{ 
                display: grid;
                grid-template-columns: repeat(7, 1fr);
                gap: 10px;
            }}
            .horario-dia {{ 
                padding: 5px;
                border: 1px solid #eee;
                border-radius: 3px;
                font-size: 12px;
            }}
            .horario-dia .dia {{ font-weight: bold; margin-bottom: 3px; }}
            .summary {{ 
                margin-bottom: 20px; 
                padding: 10px; 
                border: 1px solid #ddd; 
                border-radius: 5px;
                background-color: #f9f9f9;
            }}
            .festivo-title {{ 
                background: rgba(255, 165, 0, 0.3); 
                padding: 2px 5px; 
                border-radius: 3px; 
            }}
            .mantenimiento-title {{ 
                background: rgba(169, 169, 169, 0.3); 
                padding: 2px 5px; 
                border-radius: 3px; 
            }}
            .workers-summary {{
                margin: 20px 0;
                padding: 15px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9f9f9;
            }}
            .workers-summary h3 {{ margin-top: 0; }}
            .workers-hours-list {{
                display: flex;
                flex-wrap: wrap;
                gap: 15px;
            }}
            .worker-hours {{
                display: inline-flex;
                align-items: center;
                gap: 8px;
                font-size: 14px;
            }}
            .worker-name {{
                padding: 5px 10px;
                border-radius: 3px;
            }}
        </style>
    </head>
    <body>
        <h1>Turnos por Tienda</h1>
        <label for='tienda'>Tienda:</label>
        <select id='tienda'>
            <option value=''>Seleccione una tienda</option>
    """
    for tienda in tiendas:
        html += f"<option value='{tienda}'>{tienda}</option>"

    html += """
        </select>
        <h2 id='tienda-title'></h2>
        <div id='workers-summary' class='workers-summary'>
            <h3>Resumen de trabajadores y horas:</h3>
            <div id='workers-hours-list'></div>
        </div>
        <div id='horarios-tienda' class='horarios-tienda'>
            <h3>Horarios de la tienda por día:</h3>
            <div class='horarios-grid' id='horarios-grid'></div>
        </div>
        <div class='summary' id='summary'></div>
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
            var coloresTrabajadores = {colores_trabajadores_json};
            var coloresHorarios = {colores_horarios_json};
            var coloresEspeciales = {colores_especiales_json};
            var festivos = {festivos_json};
            var diasMantenimiento = {dias_mantenimiento_json};
            var horariosTiendas = {horarios_tiendas_json};

            // Función para actualizar el resumen de trabajadores y horas
            function actualizarResumenTrabajadores(tienda) {{
                var workersHoursList = document.getElementById('workers-hours-list');
                workersHoursList.innerHTML = '';
                
                // Obtener turnos de la tienda
                var turnosTienda = data.filter(t => t['Nombre Tienda'] === tienda);
                
                // Agrupar horas por trabajador
                var horasPorTrabajador = {{}};
                turnosTienda.forEach(turno => {{
                    if (!horasPorTrabajador[turno['Nombre']]) {{
                        horasPorTrabajador[turno['Nombre']] = 0;
                    }}
                    horasPorTrabajador[turno['Nombre']] += turno['Horas turno'];
                }});
                
                // Mostrar resumen
                Object.entries(horasPorTrabajador).forEach(([trabajador, horas]) => {{
                    var colorTrabajador = coloresTrabajadores[trabajador];
                    workersHoursList.innerHTML += `
                        <div class="worker-hours">
                            <span class="worker-name" style="background: ${{colorTrabajador}};">${{trabajador}}</span>
                            <span>${{horas.toFixed(2)}} horas</span>
                        </div>
                    `;
                }});
            }}

            // Función para mostrar horarios de la tienda
            function mostrarHorariosTienda(tienda) {{
                var horariosGrid = document.getElementById('horarios-grid');
                horariosGrid.innerHTML = '';
                
                if (horariosTiendas[tienda]) {{
                    horariosTiendas[tienda].forEach(horario => {{
                        horariosGrid.innerHTML += `
                            <div class="horario-dia">
                                <div class="dia">${{horario.Días}}</div>
                                <div>${{horario.Horario}}</div>
                            </div>
                        `;
                    }});
                }}
            }}

            // Función para marcar días especiales
            function marcarDiasEspeciales() {{
                var calendarDays = document.querySelectorAll('.day');
                calendarDays.forEach(day => {{
                    var dia = parseInt(day.getAttribute('data-day'));
                    var dayNumberDiv = day.querySelector('.day-number');
                    if (festivos.includes(dia)) {{
                        day.style.backgroundColor = coloresEspeciales.festivo;
                        dayNumberDiv.innerHTML = `${{dia}} - Festivo`;
                    }}
                    if (diasMantenimiento[tienda] && diasMantenimiento[tienda].includes(dia)) {{
                        day.style.backgroundColor = coloresEspeciales.mantenimiento;
                        dayNumberDiv.innerHTML = `${{dia}} - Mantenimiento`;
                    }}
                }});
            }}

            document.getElementById('tienda').addEventListener('change', function() {{
                var tienda = this.value;
                var calendarDays = document.querySelectorAll('.day');
                calendarDays.forEach(day => {{
                    day.style.backgroundColor = '';
                    day.innerHTML = `<div class='day-number'>${{day.getAttribute('data-day')}}</div>`;
                }});
                
                // Mostrar horarios de la tienda
                mostrarHorariosTienda(tienda);
                
                document.getElementById('tienda-title').innerHTML = `Resumen de ${{tienda}}`;
                
                var summaryHTML = `<p><span class="festivo-title"><strong>Días festivos:</strong></span> ${{festivos.map(num => num.toString()).join(', ')}}</p>`;
                if (diasMantenimiento[tienda]) {{
                    summaryHTML += `<p><span class="mantenimiento-title"><strong>Días de mantenimiento:</strong></span> ${{diasMantenimiento[tienda].map(num => num.toString()).join(', ')}}</p>`;
                }}
                document.getElementById('summary').innerHTML = summaryHTML;
                
                // Marcar días especiales (festivos y mantenimiento)
                calendarDays.forEach(day => {{
                    var dia = parseInt(day.getAttribute('data-day'));
                    var dayNumberDiv = day.querySelector('.day-number');
                    if (festivos.includes(dia)) {{
                        day.style.backgroundColor = coloresEspeciales.festivo;
                        dayNumberDiv.innerHTML = `${{dia}} - Festivo`;
                    }}
                    if (diasMantenimiento[tienda] && diasMantenimiento[tienda].includes(dia)) {{
                        day.style.backgroundColor = coloresEspeciales.mantenimiento;
                        dayNumberDiv.innerHTML = `${{dia}} - Mantenimiento`;
                    }}
                }});
                
                var turnos = data.filter(t => t['Nombre Tienda'] === tienda);
                turnos.forEach(turno => {{
                    var dayElement = document.querySelector(`.day[data-day='${{turno['Día del mes']}}']`);
                    if (dayElement) {{
                        var colorTrabajador = coloresTrabajadores[turno['Nombre']];
                        var horario = turno['Inicio turno'] + ' - ' + turno['Fin turno'];
                        var colorHorario = coloresHorarios[horario];
                        
                        dayElement.innerHTML += `
                            <div class="turno-container">
                                <div class="turno-trabajador turno-info" style="background: ${{colorTrabajador}};">${{turno['Nombre']}}</div>
                                <div class="turno-horario turno-info" style="background: ${{colorHorario}};">${{horario}}</div>
                            </div>
                        `;
                    }}
                }});
                
                // Actualizar el resumen de trabajadores y horas
                actualizarResumenTrabajadores(tienda);
            }});
        </script>
    </body>
    </html>"""

    with open('../html/turnos_tienda.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print("Archivo 'turnos_tienda.html' generado con éxito.")

if __name__ == "__main__":
    print("El script show_calendar_by_shop se está ejecutando...")
    generate_shop_calendar()
