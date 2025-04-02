# Optimización de Horas Extra

Sistema de optimización de asignación de turnos y horas extra en múltiples tiendas

## Descripción

El proyecto optimiza la asignación de turnos laborales considerando:

- Disponibilidad de empleados
- Límites de horas mensuales
- Días festivos y mantenimiento por tienda
- Vacaciones e incapacidades
- Asignación de empleados encargados

## Estructura del Proyecto

```
extra_hours_optimization/
├── config.py              # Configuración del sistema
├── create_data.py       # Generación de datos de empleados
├── data_processing.py     # Procesamiento de datos de entrada
├── main.py              # Punto de entrada principal
├── optimization.py        # Modelo de optimización
├── reports.py            # Generación de reportes
├── show_calendar_by_shop.py    # Visualización por tienda
├── show_calendar_by_worker.py  # Visualización por empleado
└── test_data_generation.py     # Generación de datos de prueba

intermediate_data/                  # Datos intermedios del proceso
├── data.csv
├── turnos_expandidos.csv
└── trabajadores.csv

outputs/                 # Resultados generados
├── asignacion_turnos.csv
├── horas_por_trabajador.csv
└── horas_por_tienda.csv

intermediate_data/       # Datos intermedios del proceso
logs/                   # Registros del sistema
html/                   # Archivos de visualización
scripts/                # Scripts adicionales
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
   cd ../extra_hours_optimization/ ; python main.py; cd ../scripts ; python show_calendar_by_worker.py
   ```

## Salidas

El sistema genera tres archivos CSV:

- `asignacion_turnos.csv`: Asignación de turnos calculada
- `horas_por_trabajador.csv`: Métricas por empleado
- `horas_por_tienda.csv`: Métricas por tienda

## Notas

- Configurado para trabajar en Enero de 2025
- Factor de 7.66 horas por día (horas semanales/6)
