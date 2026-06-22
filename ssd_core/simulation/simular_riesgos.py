import csv
import numpy as np
import pandas as pd
from datetime import datetime
import os

# 1. Cargar historial de matriculación generado por el simulador
matric_path = 'ssd_core/config/matriculacion_historica_test.csv'

if not os.path.exists(matric_path):
    print(f"[ERROR] No se encontró el archivo {matric_path}. Por favor, ejecuta primero el simulador de matriculación.")
    exit()

df = pd.read_csv(matric_path)

# Homologar nombre de columna de estudiantes si es necesario
if 'Estudiante_ID' in df.columns and 'ID_EST' not in df.columns:
    df.rename(columns={'Estudiante_ID': 'ID_EST'}, inplace=True)

# Normalizar nota a numérico para evitar errores de comparación
if 'Nota' in df.columns:
    df['Nota'] = pd.to_numeric(df['Nota'], errors='coerce')

# Detectar dinámicamente el periodo más reciente ("La Actualidad")
PERIODO_ACTUAL = df['Periodo'].max()
print(f"[INFO] Generando base de datos consolidada con corte al periodo actual: {PERIODO_ACTUAL}")

# Precalcular las cohortes de ingreso reales para riesgos externos
dict_cohortes = {}
for est_id, sub_est in df.groupby('ID_EST'):
    primer_periodo = sub_est['Periodo'].min()
    dict_cohortes[est_id] = f"O{primer_periodo}"

# =========================================================================
# 1. SIMULAR RIESGOS INTERNOS (Una sola fila por estudiante - Estado Actual)
# =========================================================================
riesgos_internos = []

# Agrupamos únicamente por ID_EST para consolidar todo su historial en una sola métrica
for estudiante_id, sub in df.groupby('ID_EST'):
    notas = sub['Nota'].astype(float)
    
    # Desempeño histórico: Promedio de absolutamente todas sus notas del historial (0-1)
    if len(notas) > 0:
        promedio = float("%s" % notas.mean())
        desempeño = round(max(0.0, min(1.0, promedio / 100.0)), 3)
    else:
        desempeño = 0.0
        
    # Repitencia Total: Cuántas matrículas adicionales tuvo el estudiante más allá del primer intento por materia
    subject_col = 'COD_ASIGNATURA' if 'COD_ASIGNATURA' in sub.columns else 'Materia'
    course_attempts = sub.groupby(subject_col).size()
    repitencia = int((course_attempts - 1).clip(lower=0).sum())
    
    # Deserción: Si el alumno registra abandono (1) en cualquier momento de su carrera
    desercion = int((sub['Abandono'] == 1).any())
    
    # Guardamos el estado actual del alumno
    riesgos_internos.append([
        PERIODO_ACTUAL,  # Corte al último año/periodo activo en el sistema
        datetime.now().strftime('%Y-%m-%d'),  # Fecha_recoleccion
        datetime.now().strftime('%Y-%m-%d'),  # Fecha_carga
        estudiante_id,
        desempeño,
        repitencia,
        desercion
    ])

# Escribir la base de datos de riesgos internos consolidada
with open('ssd_core/config/riesgos_internos.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Periodo','Fecha_recoleccion','Fecha_carga','ID_EST','desempeño','repitencia','deserción'])
    writer.writerows(riesgos_internos)


# =========================================================================
# 2. SIMULAR RIESGOS EXTERNOS (Snapshot de Egresados Reales)
# =========================================================================
# Identificar alumnos que alcanzaron el NOVENO nivel y NUNCA desertaron en su historia
estudiantes_desertores = df[df['Abandono'] == 1]['ID_EST'].unique()
egresados = df[(df["Nivel"] == "NOVENO") & (~df['ID_EST'].isin(estudiantes_desertores))]['ID_EST'].unique()

riesgos_externos = []

for estudiante_id in egresados:
    # Derivar cohorte
    id_cohorte = dict_cohortes.get(estudiante_id, f"O{PERIODO_ACTUAL}")
    
    # empleabilidad ~ N(0.8, 0.1), limitado a 0-1
    empleabilidad = np.random.normal(0.8, 0.1)
    empleabilidad = float(np.clip(empleabilidad, 0, 1))
    empleabilidad = round(empleabilidad, 3)
    
    # satisfacción laboral ~ N(0.75, 0.12), limitado a 0-1
    satisfaccion = np.random.normal(0.75, 0.12)
    satisfaccion = float(np.clip(satisfaccion, 0, 1))
    satisfaccion = round(satisfaccion, 3)
    
    riesgos_externos.append([
        PERIODO_ACTUAL,
        datetime.now().strftime('%Y-%m-%d'),
        datetime.now().strftime('%Y-%m-%d'),
        estudiante_id,
        id_cohorte,
        empleabilidad,
        satisfaccion
    ])

# Escribir riesgos externos respetando minúsculas y tildes requeridas por tu main.py
with open('ssd_core/config/riesgos_externos.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Periodo','Fecha_recoleccion','Fecha_carga','estudiante_id','ID_Cohorte','empleabilidad','satisfacción'])
    writer.writerows(riesgos_externos)

print('\n[OK] Base de datos de riesgos actualizada correctamente.')
print(f'[INFO] Estudiantes totales analizados en Riesgos Internos: {len(riesgos_internos)}')
print(f'[INFO] Egresados totales consolidados en Riesgos Externos: {len(riesgos_externos)}')