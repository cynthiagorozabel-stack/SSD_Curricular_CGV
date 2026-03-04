import csv
import random
import pandas as pd
from datetime import datetime

# Cargar historial de matriculación
matric_path = 'ssd_core/config/matriculacion_historica_test.csv'
df = pd.read_csv(matric_path)

# Simular riesgos internos
riesgos_internos = []
for estudiante_id in df['ID_EST'].unique():
    sub = df[df['ID_EST'] == estudiante_id]
    # Desempeño: promedio de notas normalizado (0-1)
    notas = sub['Nota'].astype(float)
    if len(notas) > 0:
        desempeño = round((notas.mean() - 50) / 50, 2)  # 0=50, 1=100
    else:
        desempeño = 0.0
    # Repitencia: cuenta materias reprobadas
    repitencia = (notas < 70).sum()
    # Deserción: si Abandono==1 en algún registro
    desercion = int(sub['Abandono'].max())
    riesgos_internos.append([
        '2026-1',  # Periodo
        datetime.now().strftime('%Y-%m-%d'),  # Fecha_recoleccion
        datetime.now().strftime('%Y-%m-%d'),  # Fecha_carga
        estudiante_id,
        desempeño,
        repitencia,
        desercion
    ])

with open('ssd_core/config/riesgos_internos.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Periodo','Fecha_recoleccion','Fecha_carga','ID_EST','desempeño','repitencia','deserción'])
    writer.writerows(riesgos_internos)

# Simular riesgos externos (ejemplo simple)
riesgos_externos = []
for estudiante_id in df['ID_EST'].unique():
    empleabilidad = round(random.uniform(0.5, 1.0), 2)
    satisfaccion = round(random.uniform(0.5, 1.0), 2)
    riesgos_externos.append([
        '2026-1',
        datetime.now().strftime('%Y-%m-%d'),
        datetime.now().strftime('%Y-%m-%d'),
        estudiante_id,
        empleabilidad,
        satisfaccion
    ])

with open('ssd_core/config/riesgos_externos.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Periodo','Fecha_recoleccion','Fecha_carga','ID_EST','empleabilidad','satisfacción'])
    writer.writerows(riesgos_externos)

print('Riesgos internos y externos simulados a partir de matriculación histórica.')
