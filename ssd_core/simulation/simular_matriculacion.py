
if __name__ == "__main__":
    import subprocess
    import os
    import random
    import csv
    from datetime import datetime
    import pandas as pd

    N_ESTUDIANTES_POR_COHORTE = 30  # Puedes ajustar este número
    PERIODOS = ['1', '2']
    CARRERA = 'INGENIERIA INDUSTRIAL'
    ID_CARRERA = 'INGIND1719'  # Código homologado de la malla
    ANIOS = list(range(2016, 2026))  # Últimos 10 años
    # LUGARES eliminado: solo se usa Urbano/Rural
    ESTADOS = ['Alto', 'Medio', 'Bajo']
    GENERO = ['M', 'F']
    MIN_APROBADO = 70
    MAX_REPROBADO = 2
    MAX_REPROBADO_FINAL = 3

    # Leer niveles y materias desde asignaturas.csv (separado por coma)
    asig_path = 'ssd_core/config/asignaturas.csv'
    df_asig = pd.read_csv(asig_path, sep=',')
    df_asig['NIVEL'] = df_asig['NIVEL'].str.strip().str.upper()
    NIVELES = df_asig['NIVEL'].unique().tolist()
    # MATERIAS_NIVEL: diccionario {nivel: [cod_asignatura, ...]} agrupando materias por nivel
    MATERIAS_NIVEL = {nivel: df_asig[df_asig['NIVEL'] == nivel]['COD_ASIGNATURA'].tolist() for nivel in NIVELES}
    # Diccionario para obtener RA por materia
    RA_MATERIA = dict(zip(df_asig['COD_ASIGNATURA'], df_asig['RA']))
    print(f"[DEBUG] NIVELES: {NIVELES}")
    print(f"[DEBUG] MATERIAS_NIVEL: {MATERIAS_NIVEL}")

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
                'Cohorte': anio
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
                'Periodo','Fecha_matriculacion','Fecha_carga','ID_EST','Nombre','Edad','Genero','Lugar_procedencia','ID_carrera','Carrera','Estado_sociocultural','Brecha_aprovechamiento','Nivel','Materia','Nota','Abandono'
            ])
            print(f"[DEBUG] Encabezado escrito.")
            total_rows = 0
            for est in estudiantes:
                print(f"[DEBUG] Procesando estudiante: {est['ID_EST']}")
                abandonado = 0
                abandono_nivel = est.get('Abandono_nivel')
                cohorte = est.get('Cohorte', 2022)
                # Simular avance histórico: cada año, el estudiante cursa los niveles correspondientes
                for anio_curso in range(cohorte, 2026):
                    # El estudiante solo avanza si no ha abandonado
                    if abandonado:
                        break
                    for nivel in NIVELES:
                        for periodo in PERIODOS:
                            periodo_id = f'{nivel}-{periodo}'
                            fecha_matriculacion = f'{anio_curso}-{periodo}-01'
                            fecha_carga = datetime.now().strftime('%Y-%m-%d')
                            for materia in MATERIAS_NIVEL[nivel]:
                                # Si el estudiante debe abandonar en este nivel, marcar abandono y dejar NA en adelante
                                if abandono_nivel and nivel == abandono_nivel:
                                    abandonado = 1
                                    est['Abandono'] = 1
                                if not abandonado:
                                    # Simular repitencia: si reprobó antes, puede volver a cursar
                                    nota = random.randint(50, 100)
                                    try:
                                        est['materias'][nivel][materia]['aprobado'] = nota >= MIN_APROBADO
                                        est['materias'][nivel][materia]['reprobado'] = 0 if nota >= MIN_APROBADO else 1
                                    except KeyError:
                                        print(f"[ERROR] KeyError: nivel={nivel}, materia={materia}, materias_dict={est['materias']}")
                                        continue
                                    # Homologar PERIODO: O{anio_curso}-{periodo}
                                    periodo_homologado = f"O{anio_curso}-{periodo}"
                                    # Homologar ID_ASIG: COD_ASIGNATURA
                                    id_asig = materia
                                    # Homologar RA
                                    ra = RA_MATERIA.get(materia, '')
                                    writer.writerow([
                                        periodo_homologado,
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
                                        id_asig,
                                        nota,
                                        est['Abandono']
                                    ])
                                else:
                                    periodo_homologado = f"O{anio_curso}-{periodo}"
                                    id_asig = materia
                                    ra = RA_MATERIA.get(materia, '')
                                    writer.writerow([
                                        periodo_homologado,
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
                                        id_asig,
                                        'NA',
                                        est['Abandono']
                                    ])
                                total_rows += 1
            f.flush()
            print(f"[DEBUG] Total rows written: {total_rows}")
            print(f"[DEBUG] File closed: {f.closed}")
    except Exception as e:
        print(f"[ERROR] Excepción al abrir o escribir el archivo: {e}")

    # Al finalizar la simulación de matrícula, simular riesgos internos y externos
    # subprocess.run([
    #     'C:/Users/LENOVO/Documents/Maestria_tesis/SSD_CGV_V2/venv/Scripts/python.exe',
    #     'ssd_core/simulation/simular_riesgos.py'
    # ])
