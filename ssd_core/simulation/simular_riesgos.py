import csv
import numpy as np
import pandas as pd
from datetime import datetime

# Cargar historial de matriculación
matric_path = 'ssd_core/config/matriculacion_historica_test.csv'
df = pd.read_csv(matric_path)

# 1. Simular riesgos internos
riesgos_internos = []
for estudiante_id in df['ID_EST'].unique():
    sub = df[df['ID_EST'] == estudiante_id]
    # Desempeño: promedio de notas normalizado (0-1)
    notas = sub['Nota'].astype(float)
    if len(notas) > 0:
        promedio = notas.mean()
        desempeño = (promedio - 0) / 100
        desempeño = max(0, min(1, desempeño))
        desempeño = round(desempeño, 3)
    else:
        desempeño = 0.0
    # Repitencia: materias reprobadas (nota < 70), agrupando por Materia
    if 'Materia' in sub.columns:
        materias_reprobadas = sub[sub['Nota'] < 70].drop_duplicates('Materia')
        repitencia = materias_reprobadas['Materia'].nunique()
    else:
        repitencia = (notas < 70).sum()
    # Deserción: si Abandono==1 en cualquier registro
    desercion = int((sub['Abandono'] == 1).any())
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

# 2. Identificar egresados (Nivel == "NOVENO")
egresados = df[df["Nivel"]=="NOVENO"]["ID_EST"].unique()

# 3. Simular riesgos externos SOLO para egresados
riesgos_externos = []
for estudiante_id in egresados:
    sub = df[df['ID_EST'] == estudiante_id]
    # ID_Cohorte: primer valor de Cohorte para el estudiante
    if 'Cohorte' in sub.columns:
        id_cohorte = sub['Cohorte'].iloc[0]
    else:
        id_cohorte = ''
    # empleabilidad ~ N(0.8, 0.1), limitado a 0-1
    empleabilidad = np.random.normal(0.8, 0.1)
    empleabilidad = float(np.clip(empleabilidad, 0, 1))
    empleabilidad = round(empleabilidad, 3)
    # satisfaccion_laboral ~ N(0.75, 0.12), limitado a 0-1
    satisfaccion = np.random.normal(0.75, 0.12)
    satisfaccion = float(np.clip(satisfaccion, 0, 1))
    satisfaccion = round(satisfaccion, 3)
    riesgos_externos.append([
        '2026-1',
        datetime.now().strftime('%Y-%m-%d'),
        datetime.now().strftime('%Y-%m-%d'),
        estudiante_id,
        id_cohorte,
        empleabilidad,
        satisfaccion
    ])

with open('ssd_core/config/riesgos_externos.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Periodo','Fecha_recoleccion','Fecha_carga','ID_EST','ID_Cohorte','empleabilidad','satisfaccion'])
    writer.writerows(riesgos_externos)

print('Riesgos internos y externos simulados a partir de matriculación histórica, compatibles con sistemas de soporte a la decisión.')
