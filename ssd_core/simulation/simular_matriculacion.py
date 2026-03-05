
NIVELES = [
    'PRIMER', 'SEGUNDO', 'TERCERO', 'CUARTO', 'QUINTO', 'SEXTO', 'SEPTIMO', 'OCTAVO', 'NOVENO'
]
MATERIAS_NIVEL = {
    'PRIMER': ['COMLV', 'INTII', 'QUIG1', 'DIBT1', 'CALV1', 'ALGL1'],
    'SEGUNDO': ['CALV2', 'DICAD', 'QUIG2', 'FISI1', 'EMTR1', 'IINVC'],
    'TERCERO': ['EMTR2', 'FISI2', 'TEMAT', 'EDIFE', 'CALNU', 'PROGR'],
    'CUARTO': ['EDVAL', 'RESEC', 'REMAT', 'TERMO', 'MECFL', 'INMET'],
    'QUINTO': ['ERGON', 'INVOP', 'PREST', 'INDMM', 'INMER', 'MATFI'],
    'SEXTO': ['COPRO', 'GECAL', 'LOGCS', 'OPUNI', 'PPP01', 'SHIN1', 'VINC1'],
    'SEPTIMO': ['AUTOM', 'GESAM', 'GEMAN', 'PPP02', 'PRIN1', 'SHIN2', 'VINC2'],
    'OCTAVO': ['FEPRO', 'INPR1', 'PPP03', 'PRIN2', 'SETIT', 'SIMOP'],
    'NOVENO': ['DETIT', 'DIPLA', 'GEEMP', 'INPR2', 'RELIN']
}
ANIOS = list(range(2010, 2016))
GENERO = ['M', 'F']
ESTADOS = ['Alto', 'Medio', 'Bajo']
PERIODOS = [1, 2]
MIN_APROBADO = 70
ID_CARRERA = 'INGIND1719'
CARRERA = 'INGENIERIA INDUSTRIAL'

if __name__ == "__main__":
    import subprocess
    import os
    import random
    import csv
    from datetime import datetime
    import pandas as pd
    import numpy as np
    import uuid

    N_ESTUDIANTES_POR_COHORTE = 30  # Puedes ajustar este número


    print(f"[DEBUG] NIVELES: {NIVELES}")
    print(f"[DEBUG] MATERIAS_NIVEL: {MATERIAS_NIVEL}")
    os.makedirs('ssd_core/config', exist_ok=True)


    estudiantes = []
    for anio in ANIOS:
        idx_abandono_segundo = set(random.sample(range(N_ESTUDIANTES_POR_COHORTE), int(N_ESTUDIANTES_POR_COHORTE*0.2)))
        restantes = [i for i in range(N_ESTUDIANTES_POR_COHORTE) if i not in idx_abandono_segundo]
        idx_abandono_quinto = set(random.sample(restantes, int(N_ESTUDIANTES_POR_COHORTE*0.12)))
        for i in range(N_ESTUDIANTES_POR_COHORTE):
            edad = random.randint(17, 22)
            genero = random.choice(GENERO)
            estado = random.choice(ESTADOS)
            brecha = round(random.uniform(0.1, 0.9), 2)
            procedencia = 'Urbano' if i < int(N_ESTUDIANTES_POR_COHORTE*0.6) else 'Rural'
            materias_dict = {}
            for nivel in NIVELES:
                materias_dict[nivel] = {m: {'reprobado': 0, 'aprobado': False} for m in MATERIAS_NIVEL[nivel]}
            if i in idx_abandono_segundo:
                abandono_nivel = 'SEGUNDO'
            elif i in idx_abandono_quinto:
                abandono_nivel = 'QUINTO'
            else:
                abandono_nivel = None
            # Generar ID_EST único y rastreable: E + AñoCohorte + 3 letras aleatorias + 4 dígitos aleatorios
            import string
            letras = ''.join(random.choices(string.ascii_uppercase, k=3))
            digitos = ''.join(random.choices('0123456789', k=4))
            # Asignar periodo de ingreso realista: O{anio}-1 (primer periodo del año)
            periodo_ingreso = f"O{anio}-1"
            id_est = f"E{anio}{letras}{digitos}"
            estudiantes.append({
                'ID_EST': id_est,
                'Nombre': f'Estudiante_{anio}_{i+1}',
                'Edad': edad,
                'Genero': genero,
                'Lugar_procedencia': procedencia,
                'ID_carrera': ID_CARRERA,
                'Carrera': CARRERA,
                'Estado_sociocultural': estado,
                'Brecha_aprovechamiento': brecha,
                'Abandono': 0,
                'materias': materias_dict,
                'Abandono_nivel': abandono_nivel,
                'Cohorte': periodo_ingreso,
                'Anio_Ingreso': anio,
                'Periodo_Ingreso': periodo_ingreso
            })

    # Usar solo rutas y códigos preexistentes
    output_path = os.path.abspath('ssd_core/config/matriculacion_historica_test.csv')
    print(f"[DEBUG] Writing to: {output_path}")
    # Verificar existencia y permisos antes de abrir
    if os.path.exists(output_path):
        print(f"[DEBUG] Archivo existe. Permisos: {oct(os.stat(output_path).st_mode)}")
    else:
        print(f"[DEBUG] Archivo NO existe, será creado.")
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            print(f"[DEBUG] Archivo abierto para escritura.")
            writer = csv.writer(f)
            writer.writerow([
                'Periodo','Fecha_matriculacion','Fecha_carga','ID_EST','Nombre','Edad','Genero','Lugar_procedencia','ID_carrera','Carrera','Estado_sociocultural','Brecha_aprovechamiento','Nivel','Materia','Nota','Abandono','ID_Cohorte'
            ])
            print(f"[DEBUG] Encabezado escrito.")
            total_rows = 0
            for est in estudiantes:
                print(f"[DEBUG] Procesando estudiante: {est['ID_EST']}")
                abandonado = 0
                abandono_nivel = est.get('Abandono_nivel')
                cohorte = est.get('Anio_Ingreso', 2022)
                # Si la cohorte es la más reciente, solo simular hasta OCTAVO nivel
                max_nivel = 'OCTAVO' if cohorte == max(ANIOS) else 'NOVENO'
                for anio_curso in range(cohorte, 2026):
                    if abandonado:
                        break
                    for nivel in NIVELES:
                        if max_nivel == 'OCTAVO' and nivel == 'NOVENO':
                            continue
                        for periodo in PERIODOS:
                            periodo_id = f'{nivel}-{periodo}'
                            fecha_matriculacion = f'{anio_curso}-{periodo}-01'
                            fecha_carga = datetime.now().strftime('%Y-%m-%d')
                            for materia in MATERIAS_NIVEL[nivel]:
                                if abandono_nivel and nivel == abandono_nivel:
                                    abandonado = 1
                                    est['Abandono'] = 1
                                if not abandonado:
                                    nota = random.randint(50, 100)
                                    try:
                                        est['materias'][nivel][materia]['aprobado'] = nota >= MIN_APROBADO
                                        est['materias'][nivel][materia]['reprobado'] = 0 if nota >= MIN_APROBADO else 1
                                    except KeyError:
                                        print(f"[ERROR] KeyError: nivel={nivel}, materia={materia}, materias_dict={est['materias']}")
                                        continue
                                    writer.writerow([
                                        f"O{anio_curso}-{periodo}",
                                        fecha_matriculacion,
                                        fecha_carga,
                                        est['ID_EST'],
                                        est['Nombre'],
                                        est['Edad'],
                                        est['Genero'],
                                        est['Lugar_procedencia'],
                                        est['ID_carrera'],
                                        est['Carrera'],
                                        est['Estado_sociocultural'],
                                        est['Brecha_aprovechamiento'],
                                        nivel,
                                        materia,
                                        nota,
                                        est['Abandono'],
                                        est['Cohorte']
                                    ])
                                else:
                                    writer.writerow([
                                        f"O{anio_curso}-{periodo}",
                                        fecha_matriculacion,
                                        fecha_carga,
                                        est['ID_EST'],
                                        est['Nombre'],
                                        est['Edad'],
                                        est['Genero'],
                                        est['Lugar_procedencia'],
                                        est['ID_carrera'],
                                        est['Carrera'],
                                        est['Estado_sociocultural'],
                                        est['Brecha_aprovechamiento'],
                                        nivel,
                                        materia,
                                        'NA',
                                        est['Abandono'],
                                        est['Cohorte']
                                    ])
                                total_rows += 1

            f.flush()
            print(f"[DEBUG] Total rows written: {total_rows}")
            print(f"[DEBUG] File closed: {f.closed}")
            f.flush()
            print(f"[DEBUG] Total rows written: {total_rows}")
            print(f"[DEBUG] File closed: {f.closed}")
    except Exception as e:
        print(f"[ERROR] Excepción al abrir o escribir el archivo: {e}")


    # Al finalizar la simulación de matrícula, simular riesgos externos para graduados (nivel máximo alcanzado = NOVENO) y exportar con nombre fijo
    try:
        df_matric = pd.read_csv(output_path)
        graduados = df_matric[(df_matric['Nivel'].str.upper() == 'NOVENO') & (df_matric['Nota'] != 'NA')]['ID_EST'].unique()
        print(f"[DEBUG] Primeros ID_EST de graduados: {graduados[:5]}")
        riesgos_externos = []
        fecha_hoy = datetime.now().strftime('%Y-%m-%d')
        for eid in graduados:
            empleabilidad = np.clip(np.random.normal(0.8, 0.1), 0, 1)
            satisfaccion = np.clip(np.random.normal(0.75, 0.12), 0, 1)
            riesgos_externos.append({
                'Periodo': '2026-1',
                'Fecha_recoleccion': fecha_hoy,
                'Fecha_carga': fecha_hoy,
                'estudiante_id': eid,
                'empleabilidad': round(empleabilidad, 2),
                'satisfacción': round(satisfaccion, 2)
            })
        df_riesgos_ext = pd.DataFrame(riesgos_externos)
        os.makedirs('ssd_core/config', exist_ok=True)
        riesgos_ext_path = os.path.join('ssd_core', 'config', 'riesgos_externos.csv')
        df_riesgos_ext.to_csv(riesgos_ext_path, index=False)
        print(f"[DEBUG] Riesgos externos simulados exportados a: {riesgos_ext_path}")
    except Exception as e:
        print(f"[ERROR] Error al generar riesgos externos: {e}")
