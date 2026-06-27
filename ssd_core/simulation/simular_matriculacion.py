if __name__ == "__main__":
    import os
    import random
    import csv
    from datetime import datetime
    import pandas as pd
    import numpy as np

    # === Parámetros de la simulación institucional ===
    # Estos valores se pueden ajustar desde la interfaz (Streamlit) por variable de
    # entorno. El default es exactamente el valor original del modelo, de modo que
    # sin definir nada el comportamiento es idéntico al de la versión hardcodeada.
    N_ESTUDIANTES_POR_COHORTE = int(os.environ.get('SSD_N_ESTUDIANTES_COHORTE', 25))  # Cada semestre entra un grupo nuevo y único
    CARRERA = 'Ingenieria Industrial'
    ID_CARRERA = 103
    ESTADOS = ['Alto', 'Medio', 'Bajo']
    GENERO = ['M', 'F']
    MIN_APROBADO = 70
    MAX_MATERIAS_SEMESTRE = int(os.environ.get('SSD_MAX_MATERIAS_SEMESTRE', 6))

    # 1. Cargar la estructura de la Malla desde asignaturas.csv
    asig_path = 'ssd_core/config/asignaturas.csv'
    
    if not os.path.exists(asig_path):
        # Datos de respaldo idénticos a dim_asignatura.csv si el archivo no está en el entorno de prueba
        data_malla = [
            ('PRIMER', 'ALGL1'), ('PRIMER', 'CALV1'), ('PRIMER', 'COMLV'), ('PRIMER', 'DIBT1'), ('PRIMER', 'INTII'), ('PRIMER', 'QUIG1'),
            ('SEGUNDO', 'CALV2'), ('SEGUNDO', 'DICAD'), ('SEGUNDO', 'EMTR1'), ('SEGUNDO', 'FISI1'), ('SEGUNDO', 'IINVC'), ('SEGUNDO', 'QUIG2'),
            ('TERCERO', 'CALNU'), ('TERCERO', 'EDIFE'), ('TERCERO', 'EMTR2'), ('TERCERO', 'FISI2'), ('TERCERO', 'PROGR'), ('TERCERO', 'TEMAT'),
            ('CUARTO', 'EDVAL'), ('CUARTO', 'INMET'), ('CUARTO', 'MECFL'), ('CUARTO', 'RESEC'), ('CUARTO', 'REMAT'), ('CUARTO', 'TERMO'),
            ('QUINTO', 'ERGON'), ('QUINTO', 'INDMM'), ('QUINTO', 'INMER'), ('QUINTO', 'INVOP'), ('QUINTO', 'MATFI'), ('QUINTO', 'PREST'),
            ('SEXTO', 'COPRO'), ('SEXTO', 'GECAL'), ('SEXTO', 'LOGCS'), ('SEXTO', 'OPUNI'), ('SEXTO', 'PPP01'), ('SEXTO', 'SHIN1'), ('SEXTO', 'VINC1'),
            ('SEPTIMO', 'AUTOM'), ('SEPTIMO', 'GESAM'), ('SEPTIMO', 'GEMAN'), ('SEPTIMO', 'PPP02'), ('SEPTIMO', 'PRIN1'), ('SEPTIMO', 'SHIN2'), ('SEPTIMO', 'VINC2'),
            ('OCTAVO', 'FEPRO'), ('OCTAVO', 'INPR1'), ('OCTAVO', 'PPP03'), ('OCTAVO', 'PRIN2'), ('OCTAVO', 'SETIT'), ('OCTAVO', 'SIMOP'),
            ('NOVENO', 'DETIT'), ('NOVENO', 'DIPLA'), ('NOVENO', 'GEEMP'), ('NOVENO', 'INPR2'), ('NOVENO', 'RELIN')
        ]
        df_asig = pd.DataFrame(data_malla, columns=['NIVEL', 'COD_ASIGNATURA'])
    else:
        df_asig = pd.read_csv(asig_path, sep=';' if ';' in open(asig_path).read() else ',')
        if 'Nivel' in df_asig.columns: df_asig.rename(columns={'Nivel': 'NIVEL'}, inplace=True)
        if 'Asignatura_id' in df_asig.columns: df_asig.rename(columns={'Asignatura_id': 'COD_ASIGNATURA'}, inplace=True)

    df_asig['NIVEL'] = df_asig['NIVEL'].str.strip().str.upper()
    NIVELES_ORDENADOS = ['PRIMER', 'SEGUNDO', 'TERCERO', 'CUARTO', 'QUINTO', 'SEXTO', 'SEPTIMO', 'SÉPTIMO', 'OCTAVO', 'NOVENO']
    NIVELES = [n for n in NIVELES_ORDENADOS if n in df_asig['NIVEL'].unique()]
    MATERIAS_NIVEL = {nivel: df_asig[df_asig['NIVEL'] == nivel]['COD_ASIGNATURA'].tolist() for nivel in NIVELES}

    # Red de Prerrequisitos de la Universidad Técnica de Manabí (Malla Industrial)
    PRERREQUISITOS = {
        'CALV2': ['CALV1'], 'FISI2': ['FISI1'], 'QUIG2': ['QUIG1'],
        'EMTR2': ['EMTR1'], 'INMET': ['EMTR2'], 'SHIN2': ['SHIN1'],
        'INPR2': ['INPR1'], 'DETIT': ['SETIT'], 'EDIFE': ['CALV2'],
        'MECFL': ['FISI2'], 'TERMO': ['FISI2'], 'SIMOP': ['INVOP'],
        'PPP02': ['PPP01'], 'PPP03': ['PPP02'], 'VINC2': ['VINC1']
    }

    # 2. Definición de la Línea de Tiempo Institucional (Ecosistema Concurrente)
    # Año de inicio y de fin de la ventana de simulación. Parametrizables desde la
    # interfaz; default = ventana original del modelo (2018-2026).
    ANIO_INICIO = int(os.environ.get('SSD_ANIO_INICIO', 2018))
    ANIO_FIN = int(os.environ.get('SSD_ANIO_FIN', 2026))
    PERIODOS_ACADEMICOS = []
    for anio in range(ANIO_INICIO, ANIO_FIN + 1):
        PERIODOS_ACADEMICOS.append(f"{anio}-1")
        PERIODOS_ACADEMICOS.append(f"{anio}-2")

    estudiantes = []
    id_contador = 1

    # Pre-crear y registrar todas las cohortes únicas que ingresarán en sus respectivos años
    for periodo_ingreso in PERIODOS_ACADEMICOS:
        # Dejamos de ingresar nuevas cohortes en el último año de la ventana para no
        # saturar con datos incompletos. Atado a ANIO_FIN (default 2026 -> corte 2025),
        # así el corte se mueve con el parámetro en vez de quedar fijo en 2025.
        if int(periodo_ingreso.split('-')[0]) > ANIO_FIN - 1:
            continue
            
        for _ in range(N_ESTUDIANTES_POR_COHORTE):
            brecha = round(random.uniform(0.1, 0.9), 2)
            # Capacidad académica ligada al perfil socio-educativo (Evita notas 100% al azar)
            capacidad_base = 88 - (brecha * 30) 
            
            historial_materias = {}
            for nivel in NIVELES:
                for m in MATERIAS_NIVEL[nivel]:
                    historial_materias[m] = {'reprobaciones': 0, 'aprobado': False, 'nivel': nivel}

            # Riesgo natural de deserción institucional planificada (simulación de eventos externos)
            rand_dropout = random.random()
            abandono_planificado = 'SEGUNDO' if rand_dropout < 0.12 else ('QUINTO' if rand_dropout < 0.20 else None)

            estudiantes.append({
                'Estudiante_ID': f'E{id_contador}',
                'Nombre': f'Estudiante_{id_contador}',
                'Edad': random.randint(17, 21),
                'Genero': random.choice(GENERO),
                'Lugar_procedencia': 'Urbano' if random.random() < 0.6 else 'Rural',
                'ID_carrera': ID_CARRERA,
                'Carrera': CARRERA,
                'Estado_sociocultural': random.choice(ESTADOS),
                'Brecha_aprovechamiento': brecha,
                'capacidad': capacidad_base,
                'Abandono': 0,
                'Abandono_nivel_planificado': abandono_planificado,
                'Periodo_Ingreso': periodo_ingreso,
                'materias': historial_materias
            })
            id_contador += 1

    # 3. Motor de Ejecución en Tiempo Real (Simulación Transversal por Periodo)
    output_path = os.path.abspath('ssd_core/config/matriculacion_historica_test.csv')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Periodo','Fecha_matriculacion','Fecha_carga','Estudiante_ID','Nombre','Edad','Genero',
            'Lugar_procedencia','ID_carrera','Carrera','Estado_sociocultural','Brecha_aprovechamiento',
            'Nivel','Materia','Nota','Abandono'
        ])

        total_rows = 0

        # El reloj institucional avanza semestre a semestre
        for periodo_actual in PERIODOS_ACADEMICOS:
            anio_act, per_act = periodo_actual.split('-')
            fecha_mat = f"{anio_act}-03-01" if per_act == '1' else f"{anio_act}-09-01"
            fecha_carga = datetime.now().strftime('%Y-%m-%d')

            # Procesar en paralelo a TODOS los estudiantes de TODAS las cohortes vigentes
            for est in estudiantes:
                # El estudiante solo se procesa si ya ingresó cronológicamente y si no ha desertado antes
                idx_actual = PERIODOS_ACADEMICOS.index(periodo_actual)
                idx_ingreso = PERIODOS_ACADEMICOS.index(est['Periodo_Ingreso'])
                
                if est['Abandono'] == 1 or idx_actual < idx_ingreso:
                    continue

                # Calcular qué materias le faltan por aprobar
                materias_pendientes = [m for m, info in est['materias'].items() if not info['aprobado']]
                
                if not materias_pendientes:
                    continue # El estudiante ya completó la malla con éxito (Graduado)

                # Determinación del "Nivel Institucional del Estudiante" para este periodo exacto
                # Se define por el nivel más bajo donde aún arrastra materias pendientes
                nivel_actual_estudiante = est['materias'][materias_pendientes[0]]['nivel']

                # Control de deserción planificada por nivel
                if est['Abandono_nivel_planificado'] == nivel_actual_estudiante:
                    est['Abandono'] = 1
                    continue

                # Selección de asignaturas cumpliendo Prerrequisitos de la UTM
                materias_disponibles = []
                for mat in materias_pendientes:
                    info = est['materias'][mat]
                    if info['reprobaciones'] < 3:
                        reqs = PRERREQUISITOS.get(mat, [])
                        cumple_prerrequisitos = all(est['materias'][r]['aprobado'] for r in reqs)
                        if cumple_prerrequisitos:
                            materias_disponibles.append(mat)

                # Limitar la carga académica por semestre a un máximo real (6 asignaturas)
                materias_a_matricular = materias_disponibles[:MAX_MATERIAS_SEMESTRE]

                # Simular las notas del semestre para este estudiante
                for materia in materias_a_matricular:
                    info_mat = est['materias'][materia]
                    
                    # Campana de Gauss basada en el perfil del alumno (notas consistentes con su capacidad)
                    nota = int(np.clip(np.random.normal(est['capacidad'], 6), 48, 100))
                    
                    if nota >= MIN_APROBADO:
                        info_mat['aprobado'] = True
                    else:
                        info_mat['reprobaciones'] += 1
                        # REGLA INSTITUCIONAL: Si reprueba por 3ra vez, la 4ta matrícula se bloquea y es expulsado
                        if info_mat['reprobaciones'] >= 3:
                            est['Abandono'] = 1

                    # Calcular edad exacta en base al tiempo transcurrido en semestres
                    edad_dinamica = est['Edad'] + (idx_actual - idx_ingreso) // 2

                    # Escribir el registro histórico nativo
                    writer.writerow([
                        periodo_actual,
                        fecha_mat,
                        fecha_carga,
                        est['Estudiante_ID'],
                        est['Nombre'],
                        edad_dinamica,
                        est['Genero'],
                        est['Lugar_procedencia'],
                        est['ID_carrera'],
                        est['Carrera'],
                        est['Estado_sociocultural'],
                        est['Brecha_aprovechamiento'],
                        nivel_actual_estudiante,  # El nivel asignado al grupo en este tiempo real
                        materia,
                        nota,
                        est['Abandono']
                    ])
                    total_rows += 1

                    # Romper el semestre del estudiante si cae en causal de deserción reglamentaria
                    if est['Abandono'] == 1:
                        break

    print(f"[OK] Simulación finalizada.")
    print(f"[INFO] Registros históricos generados en paralelo: {total_rows}")