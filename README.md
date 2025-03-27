# Optimización de Horas Extra

Sistema de optimización de asignación de turnos y horas extra en múltiples tiendas

## Descripción

El proyecto asignación turnos laborales y horas extra considerando las siguientes restricciones:

- Disponibilidad de empleados
- Límites de horas mensuales
- Días festivos y mantenimiento por tienda
- Vacaciones e incapacidades por empleado
- Asignación de empleados encargados por tienda

## Estructura del Proyecto

```
extra_hours_optimization/
├── data_processing.py    # Procesamiento de datos de entrada
├── optimization.py       # Modelo de optimización
├── reports.py           # Generación de reportes
├── main.py             # Punto de entrada principal
└── logger.py           # Configuración de logging

inputs/
├── data.csv
└── trabajadores.csv

outputs/
├── asignacion_turnos.csv
├── horas_por_trabajador.csv
└── horas_por_tienda.csv

scripts/
├── create_data.py
├── show_calendar_by_shop.py
├── show_calendar_by_worker.py
├── what_holidays.py
└── how_many_days.py

```

## Scripts Adicionales Disponibles

### create_data.py

Genera el archivo `empleados_horas.csv` con la información de disponibilidad de los empleados, incluyendo:

- Días de descanso
- Días de incapacidad
- Días de vacaciones
- Horas disponibles por mes
- Horas extra disponibles

### show_calendar_by_worker.py

Genera una visualización HTML (`turnos_empleado.html`) que muestra:

- Calendario mensual por empleado
- Resumen de productividad
- Horas trabajadas y disponibles
- Tiendas asignadas
- Días de descanso, vacaciones e incapacidad

## Uso

1. Configura los datos de entrada en la carpeta `inputs/`
2. Ajusta los parámetros en `main.py`:
   ```python
   init_data = {
       'holidays_are_availables': {'T_MB': False, 'T_EC': True, 'T_CT': True},
       'maintenance_days_by_store': {},
       'month': 1,
       'year': 2025,
       'country': "CO"
   }
   ```
3. Ejecuta el programa:
   ```bash
   python main.py
   ```

## Salidas

El sistema genera tres archivos CSV:

- `asignacion_turnos.csv`: Asignación de turnos calculada
- `horas_por_trabajador.csv`: Metricas por empleado
- `horas_por_tienda.csv`: Metricas por tienda

## Características Principales

- Optimización de asignación de turnos
- Manejo de horas extra
- Consideración de días festivos y mantenimiento
- Reportes detallados por trabajador y tienda

## Notas

- El proyecto está configurado para trabajar en Enero de 2025
- Los cálculos de horas consideran un factor de 7.66 horas por día, eso tomando las horas por semana divididas entre 6, para considerar un dia de descanso
