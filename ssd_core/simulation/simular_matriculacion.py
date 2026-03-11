
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
ANIOS = list(range(2010, 2027))  # 2010 a 2026 inclusive
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

    N_ESTUDIANTES_POR_COHORTE = 35  # Ajuste solicitado: 35 estudiantes por cohorte


    print(f"[DEBUG] NIVELES: {NIVELES}")
    print(f"[DEBUG] MATERIAS_NIVEL: {MATERIAS_NIVEL}")
    os.makedirs('ssd_core/config', exist_ok=True)


    estudiantes = []
    for anio in ANIOS:
        # Cohortes antiguas (2010-2014): mayoría graduados
        if anio <= 2014:
            abandono_segundo = int(N_ESTUDIANTES_POR_COHORTE * 0.05)  # pocos abandonan temprano
            abandono_quinto = int(N_ESTUDIANTES_POR_COHORTE * 0.05)
            max_nivel = 'NOVENO'
        # Cohortes intermedias (2015-2021): niveles intermedios
        elif 2015 <= anio <= 2021:
            abandono_segundo = int(N_ESTUDIANTES_POR_COHORTE * 0.12)
            abandono_quinto = int(N_ESTUDIANTES_POR_COHORTE * 0.10)
            max_nivel = random.choice(['TERCERO','CUARTO','QUINTO','SEXTO','SEPTIMO','OCTAVO'])
        # Cohortes recientes (2022-2026): solo primeros niveles
        else:
            abandono_segundo = int(N_ESTUDIANTES_POR_COHORTE * 0.15)
            abandono_quinto = 0
            max_nivel = random.choice(['PRIMER','SEGUNDO','TERCERO'])

        idx_abandono_segundo = set(random.sample(range(N_ESTUDIANTES_POR_COHORTE), abandono_segundo))
        restantes = [i for i in range(N_ESTUDIANTES_POR_COHORTE) if i not in idx_abandono_segundo]
        idx_abandono_quinto = set(random.sample(restantes, abandono_quinto))
        for i in range(N_ESTUDIANTES_POR_COHORTE):
            edad = random.randint(17, 22)
            genero = random.choice(GENERO)
            estado = random.choice(ESTADOS)
            brecha = round(random.uniform(0.1, 0.9), 2)
            procedencia = 'Urbano' if i < int(N_ESTUDIANTES_POR_COHORTE*0.6) else 'Rural'
            materias_dict = {}
            for nivel in NIVELES:
                materias_dict[nivel] = {m: {'reprobado': 0, 'aprobado': False} for m in MATERIAS_NIVEL[nivel]}
            # Asignar abandono según reglas
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
                'Periodo_Ingreso': periodo_ingreso,
                'Max_nivel': max_nivel
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
        # Crear tres archivos: académico, sociodemográfico fijo, y contexto por periodo
        output_academico = os.path.abspath('ssd_core/config/matriculacion_historica_test.csv')
        output_sociodemo = os.path.abspath('ssd_core/config/datos_sociodemograficos_test.csv')
        output_contexto = os.path.abspath('ssd_core/config/contexto_periodo_test.csv')
        with open(output_academico, 'w', newline='', encoding='utf-8') as f_acad, \
             open(output_sociodemo, 'w', newline='', encoding='utf-8') as f_soc, \
             open(output_contexto, 'w', newline='', encoding='utf-8') as f_ctx:
            writer_acad = csv.writer(f_acad)
            writer_soc = csv.writer(f_soc)
            writer_ctx = csv.writer(f_ctx)
            # Encabezados
            writer_acad.writerow([
                'Periodo','Fecha_matriculacion','Fecha_carga','ID_EST','ID_carrera','Nivel','COD_ASIGNATURA','Nota','ID_Cohorte','Abandono'
            ])
            writer_soc.writerow([
                'Genero','Fecha_nacimiento','Lugar_procedencia','ID_carrera','ID_EST','Nombre','B_Aprovechamiento_Inicial','autoidentificacion_etnica','ID_Cohorte'
            ])
            writer_ctx.writerow([
                'Estado_sociocultural','Alerta_Violeta_General','Alerta_V_Universitaria',
                'Periodo','Fecha_matriculacion','Fecha_carga','ID_EST','ID_carrera','Edad','ID_Cohorte'
            ])
            total_rows_acad = 0
            total_rows_soc = 0
            total_rows_ctx = 0
            estudiantes_soc = set()
            for est in estudiantes:
                abandonado = 0
                abandono_nivel = est.get('Abandono_nivel')
                cohorte = est.get('Anio_Ingreso', 2022)
                # Calcular fecha de nacimiento coherente con edad y año de ingreso (asume ingreso en marzo)
                fecha_nacimiento = f"{cohorte - est['Edad']}-03-01"
                # Simular autoidentificación étnica (única por estudiante)
                etnias = ['mestizo', 'blanco', 'montubio', 'indigena', 'afroecuatoriana']
                autoidentificacion_etnica = random.choices(etnias, weights=[0.7,0.1,0.07,0.08,0.05])[0]
                # Escribir solo una vez los datos sociodemográficos fijos
                if est['ID_EST'] not in estudiantes_soc:
                    writer_soc.writerow([
                        est['Genero'],
                        fecha_nacimiento,
                        est['Lugar_procedencia'],
                        est['ID_carrera'],
                        est['ID_EST'],
                        est['Nombre'],
                        est['Brecha_aprovechamiento'],
                        autoidentificacion_etnica,
                        est['Cohorte']
                    ])
                    estudiantes_soc.add(est['ID_EST'])
                    total_rows_soc += 1
                # Simular avance académico según tipo de cohorte
                max_nivel = est.get('Max_nivel', 'NOVENO')
                niveles_a_simular = NIVELES[:NIVELES.index(max_nivel)+1]
                for anio_curso in range(est['Anio_Ingreso'], 2027):
                    if abandonado:
                        break
                    for nivel in niveles_a_simular:
                        # Si el estudiante abandonó, no simular más niveles
                        if abandono_nivel and nivel == abandono_nivel:
                            abandonado = 1
                            est['Abandono'] = 1
                        for periodo in PERIODOS:
                            periodo_id = f'{nivel}-{periodo}'
                            fecha_matriculacion = f'{anio_curso}-{periodo}-01'
                            fecha_carga = datetime.now().strftime('%Y-%m-%d')
                            edad_actual = est['Edad'] + (anio_curso - est['Anio_Ingreso'])
                            for materia in MATERIAS_NIVEL[nivel]:
                                # Archivo académico
                                if not abandonado:
                                    nota = random.randint(50, 100)
                                    try:
                                        est['materias'][nivel][materia]['aprobado'] = nota >= MIN_APROBADO
                                        est['materias'][nivel][materia]['reprobado'] = 0 if nota >= MIN_APROBADO else 1
                                    except KeyError:
                                        print(f"[ERROR] KeyError: nivel={nivel}, materia={materia}, materias_dict={est['materias']}" )
                                        continue
                                    writer_acad.writerow([
                                        f"O{anio_curso}-{periodo}",
                                        fecha_matriculacion,
                                        fecha_carga,
                                        est['ID_EST'],
                                        est['ID_carrera'],
                                        nivel,
                                        materia,
                                        nota,
                                        est['Cohorte'],
                                        est['Abandono']
                                    ])
                                else:
                                    writer_acad.writerow([
                                        f"O{anio_curso}-{periodo}",
                                        fecha_matriculacion,
                                        fecha_carga,
                                        est['ID_EST'],
                                        est['ID_carrera'],
                                        nivel,
                                        materia,
                                        'NA',
                                        est['Cohorte'],
                                        est['Abandono']
                                    ])
                                total_rows_acad += 1
                                # Archivo de contexto por periodo (una fila por periodo, no por materia)
                                if materia == MATERIAS_NIVEL[nivel][0]:
                                    alerta_violeta_general = random.randint(1, 5)
                                    alerta_v_universitaria = random.randint(1, 5)
                                    writer_ctx.writerow([
                                        est['Estado_sociocultural'],
                                        alerta_violeta_general,
                                        alerta_v_universitaria,
                                        f"O{anio_curso}-{periodo}",
                                        fecha_matriculacion,
                                        fecha_carga,
                                        est['ID_EST'],
                                        est['ID_carrera'],
                                        edad_actual,
                                        est['Cohorte']
                                    ])
                                    total_rows_ctx += 1
            f_acad.flush()
            f_soc.flush()
            f_ctx.flush()
            print(f"[DEBUG] Total rows written (acad): {total_rows_acad}")
            print(f"[DEBUG] Total rows written (soc): {total_rows_soc}")
            print(f"[DEBUG] Total rows written (ctx): {total_rows_ctx}")
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
