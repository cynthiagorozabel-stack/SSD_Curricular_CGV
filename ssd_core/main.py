# main.py
import os
import pandas as pd
from ssd_core.base.config_loader import ConfigLoader
from ssd_core.base.data_loader import DataLoader
from ssd_core.base.audit_trail import AuditTrail
from ssd_core.base.ssd_runner import SSDRunner
from ssd_core.engines.ra_engine import RAEngine
from ssd_core.engines.competencia_engine import CompetenciaEngine
from ssd_core.engines.perfil_engine import PerfilEngine
from ssd_core.engines.external_risk_engine import ExternalRiskEngine
from ssd_core.engines.internal_risk_engine import InternalRiskEngine
from ssd_core.engines.beg_engine import BEGEngine
from ssd_core.engines.ispg_engine import ISPGEngine
from ssd_core.engines.normalizacion_engine import NormalizacionEngine
from ssd_core.validation.cronbach import CronbachValidator
from ssd_core.validation.sensibilidad import SensibilidadValidator
from ssd_core.validation.montecarlo import MonteCarloValidator
from ssd_core.export.powerbi_export import ExportEngine
from ssd_core.export.advanced_export import export_advanced

def main(carrera_id):
    # ...existing code...
    # Paths
    config_path = os.path.join('ssd_core', 'config', 'model_config.yaml')
    ra_path = os.path.join('ssd_core', 'config', 'ra_competencia.csv')
    competencia_path = os.path.join('ssd_core', 'config', 'dim_competencia.csv')
    perfil_path = os.path.join('ssd_core', 'config', 'competencia_perfil.csv')
    riesgos_internos_path = os.path.join('ssd_core', 'config', 'riesgos_internos.csv')
    riesgos_externos_path = os.path.join('ssd_core', 'config', 'riesgos_externos.csv')
    audit_dir = 'audit'
    export_dir = 'export'

    # Loaders
    config_loader = ConfigLoader(config_path)
    config = config_loader.load()
    config_loader.validate()
    ra_data = DataLoader(ra_path).load()
    if 'competencia_id' in ra_data.columns:
        ra_data = ra_data.rename(columns={'competencia_id': 'ID_COMP'})
    competencia_data = DataLoader(competencia_path).load()
    if 'ID_Competencia' in competencia_data.columns:
        competencia_data = competencia_data.rename(columns={'ID_Competencia': 'ID_COMP'})
    perfil_data = DataLoader(perfil_path).load()
    riesgos_internos = DataLoader(riesgos_internos_path).load()
    # Homologar columna ID_EST en riesgos_internos
    if 'estudiante_id' in riesgos_internos.columns and 'ID_EST' not in riesgos_internos.columns:
        riesgos_internos['ID_EST'] = riesgos_internos['estudiante_id']
    # Si no existe ninguna, intentar poblarla desde riesgos_int_export si es posible
    if 'ID_EST' not in riesgos_internos.columns and 'ID_EST' in locals() and not riesgos_int_export.empty:
        riesgos_internos = riesgos_internos.assign(ID_EST=riesgos_int_export['ID_EST'])
    # Si aún no existe, poner NA
    if 'ID_EST' not in riesgos_internos.columns:
        riesgos_internos['ID_EST'] = 'NA'
    riesgos_externos = DataLoader(riesgos_externos_path).load()

    # Engines
    ra_engine = RAEngine(ra_data)
    competencia_engine = CompetenciaEngine(competencia_data, ra_data)
    competencia_results = competencia_engine.calculate(student_id=None)
    perfil_engine = PerfilEngine(perfil_data, competencia_results)
    perfil_results = perfil_engine.calculate()
    external_risk_engine = ExternalRiskEngine(riesgos_externos)
    internal_risk_engine = InternalRiskEngine(riesgos_internos)
    # Eliminados: beg_engine, ispg_engine, normalizacion_engine (no se usan)

    # Validaciones (solo Cronbach sobre la matriz de logros)
    sensibilidad = None
    montecarlo = None

    # Auditoría
    audit_trail = AuditTrail(audit_dir)
    config_hash = audit_trail.hash_file(config_path)
    data_hash = audit_trail.hash_file(ra_path)
    run_id = audit_trail.register(config_hash, data_hash, carrera_id, config['version_modelo'])


    # =====================
    # Exportar logros individuales (RA, competencia, perfil, riesgos internos)
    # =====================
    import numpy as np
    # Cargar datos necesarios
    matric = pd.read_csv('ssd_core/config/matriculacion_historica_test.csv')
    asig = pd.read_csv('ssd_core/config/asignaturas.csv')
    comp_perfil = pd.read_csv('ssd_core/config/competencia_perfil.csv')
    # Homologar columnas de ID
    matric = matric.rename(columns={'Estudiante_ID':'ID_EST'})
    comp_perfil = comp_perfil.rename(columns={'competencia_id': 'ID_COMP'})
    # Mapear materias a RA
    materia_ra = asig.set_index('COD_ASIGNATURA')['RA'].to_dict()
    matric['RA'] = matric['Materia'].map(materia_ra)
    # Filtrar solo filas con RA válido y nota numérica
    matric = matric[matric['RA'].notnull() & matric['Nota'].apply(lambda x: str(x).replace('.','',1).isdigit())]
    matric['Nota'] = matric['Nota'].astype(float)
    # Calcular nivel de logro por estudiante y RA (promedio de notas)
    ra_logro = matric.groupby(['ID_EST','RA']).agg({'Nota':'mean'}).reset_index()
    ra_logro = ra_logro.rename(columns={'Nota':'Logro_RA'})
    ra_logro['Fecha_corte'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    # Calcular logro de competencia por estudiante
    comp_logro = []
    for est in ra_logro['ID_EST'].unique():
        est_ra = ra_logro[ra_logro['ID_EST']==est]
        for comp in comp_perfil['ID_COMP'].unique():
            # Buscar todos los RA asociados a esta competencia
            ra_asociados = asig[(asig['RA'].notnull()) & (asig['RA'].str.startswith('RA')) & (asig['RA'].isin(est_ra['RA']))]['RA'].unique().tolist()
            ra_vals = est_ra[est_ra['RA'].isin(ra_asociados)]['Logro_RA']
            if not ra_vals.empty:
                comp_logro.append({'ID_EST':est, 'ID_COMP':comp, 'Logro_Competencia':ra_vals.mean(), 'Fecha_corte':pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')})
    comp_logro = pd.DataFrame(comp_logro)
    # Calcular perfil por estudiante (suma ponderada de competencias)
    # Primero, asignar ID_Cohorte a cada estudiante usando su primer periodo de ingreso
    # Extraer periodo de ingreso real desde matriculacion_historica_test.csv
    primer_periodo = matric.groupby('ID_EST')['Periodo'].first().to_dict()
    # Calcular perfil y asignar cohorte
    perfil_logro = []
    for est in comp_logro['ID_EST'].unique():
        est_comp = comp_logro[comp_logro['ID_EST']==est]
        id_cohorte = primer_periodo.get(est, '')
        for perfil in comp_perfil['perfil_id'].unique():
            compas = comp_perfil[comp_perfil['perfil_id']==perfil]['ID_COMP']
            vals = est_comp[est_comp['ID_COMP'].isin(compas)]['Logro_Competencia']
            if not vals.empty:
                perfil_logro.append({
                    'ID_EST':est,
                    'ID_PERFIL':perfil,
                    'Logro_Perfil':vals.mean(),
                    'Fecha_corte':pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'ID_Cohorte':id_cohorte
                })
    perfil_logro = pd.DataFrame(perfil_logro)
    # Calcular riesgos internos individuales desde el historial de matrícula
    # Desempeño: promedio de notas válidas
    # Repitencia: materias con más de una nota registrada
    # Deserción: suma de Abandono==1
    def safe_float(x):
        try:
            return float(x)
        except:
            return np.nan
    matric['Nota_num'] = matric['Nota'].apply(safe_float)
    riesgos_calc = []
    for est, grupo in matric.groupby('ID_EST'):
        notas_validas = grupo['Nota_num'].dropna()
        desempeno = notas_validas.mean() if not notas_validas.empty else np.nan
        repitencia = grupo.groupby('Materia').size()
        repitencia = (repitencia > 1).sum()
        desercion = grupo['Abandono'].fillna(0).astype(int).sum()
        riesgos_calc.append({'ID_EST': est, 'desempeño': round(desempeno,2) if not np.isnan(desempeno) else '', 'repitencia': repitencia, 'deserción': desercion})
    riesgos_int_export = pd.DataFrame(riesgos_calc)
    # Exportar archivos
    ra_logro.to_csv('export/ra_logro_individual.csv', index=False)
    comp_logro.to_csv('export/competencia_logro_individual.csv', index=False)
    perfil_logro.to_csv('export/perfil_logro_individual.csv', index=False)
    # Sobrescribir riesgos internos individuales siempre
    # Añadir trazabilidad a riesgos internos: ID_Cohorte y Fecha_corte
    if not perfil_logro.empty:
        perfil_idx = perfil_logro.set_index('ID_EST')
        riesgos_int_export['ID_Cohorte'] = riesgos_int_export['ID_EST'].map(perfil_idx['ID_Cohorte']) if 'ID_Cohorte' in perfil_idx.columns else ''
        riesgos_int_export['Fecha_corte'] = riesgos_int_export['ID_EST'].map(perfil_idx['Fecha_corte']) if 'Fecha_corte' in perfil_idx.columns else ''
    riesgos_int_export.to_csv('export/riesgos_internos_individual.csv', index=False)
    print('Exportados: ra_logro_individual.csv, competencia_logro_individual.csv, perfil_logro_individual.csv, riesgos_internos_individual.csv')

    # =====================
    # Exportar matriz de logros individuales y riesgos externos individuales
    # =====================
    # Matriz de logros RA (estudiante x RA)
    ra_matrix = ra_logro.pivot(index='ID_EST', columns='RA', values='Logro_RA')
    # Agregar desempeño, repitencia, deserción, perfil, periodo, fechas
    # Desempeño, repitencia, deserción ya calculados en riesgos_int_export
    perfil_logro_idx = perfil_logro.set_index('ID_EST') if 'ID_EST' in perfil_logro.columns else pd.DataFrame()
    # Unir todo
    full_matrix = ra_matrix.copy()
    for col in ['desempeño','repitencia','deserción']:
        if col in riesgos_int_export.set_index('ID_EST').columns:
            full_matrix[col] = riesgos_int_export.set_index('ID_EST')[col]
    if 'Logro_Perfil' in perfil_logro_idx.columns:
        full_matrix['Logro_Perfil'] = perfil_logro_idx['Logro_Perfil']
    if 'ID_PERFIL' in perfil_logro_idx.columns:
        full_matrix['ID_PERFIL'] = perfil_logro_idx['ID_PERFIL']
    # Agregar columnas de logros por competencia para cada estudiante
    if not comp_logro.empty:
        comp_matrix = comp_logro.pivot(index='ID_EST', columns='ID_COMP', values='Logro_Competencia')
        # Renombrar columnas para que sean claras (por ejemplo: COMP_<ID_COMP>)
        comp_matrix.columns = [f'COMP_{col}' for col in comp_matrix.columns]
        # Unir con la matriz principal
        full_matrix = full_matrix.join(comp_matrix, how='left')
    # Periodo y fechas (usamos la última fecha de corte de cada estudiante)
    if 'Fecha_corte' in perfil_logro_idx.columns:
        full_matrix['Fecha_corte'] = perfil_logro_idx['Fecha_corte']
    # Reset index para tener ID_EST como columna
    full_matrix = full_matrix.reset_index()
    # Exportar
    full_matrix.to_csv('export/ra_logro_matrix.csv', index=False)
    print('Exportado: export/ra_logro_matrix.csv')

    # Calcular alfa de Cronbach y Monte Carlo solo sobre la matriz de logros (ignorando columnas no numéricas)
    # Seleccionar solo columnas numéricas (RA, desempeño, etc.)
    matrix_numeric = full_matrix.select_dtypes(include=['number'])
    if matrix_numeric.shape[1] >= 2:
        cronbach_validator = CronbachValidator(matrix_numeric)
        alpha = cronbach_validator.calculate_alpha()
        montecarlo_validator = MonteCarloValidator(matrix_numeric)
        montecarlo = montecarlo_validator.simulate()
    else:
        alpha = None
        montecarlo = None

    # Exportar alpha de Cronbach con trazabilidad directamente desde aquí
    try:
        pipeline_name = "main_pipeline"  # Cambia esto si tu pipeline tiene otro nombre
        if alpha is not None and run_id is not None:
            import json
            from datetime import datetime
            data = {
                "run_id": run_id,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "pipeline": pipeline_name,
                "alpha_cronbach": alpha
            }
            out_path = os.path.join("export", f"alpha_cronbach_{run_id}.json")
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print(f"Exportado: {out_path}")
    except Exception as e:
        print(f"[WARN] No se pudo exportar alpha_cronbach automáticamente: {e}")

    # Exportar riesgos externos individuales (estudiante x riesgo)
    # Buscar el archivo de riesgos externos con el run_id actual
    riesgos_ext_path = f'export/riesgos_externos_{run_id}.csv'
    if os.path.exists(riesgos_ext_path):
        riesgos_ext = pd.read_csv(riesgos_ext_path)
        # Añadir trazabilidad a riesgos externos: ID_Cohorte y Fecha_corte
        if not perfil_logro.empty:
            perfil_idx = perfil_logro.set_index('ID_EST')
            riesgos_ext['ID_Cohorte'] = riesgos_ext['estudiante_id'].map(perfil_idx['ID_Cohorte']) if 'ID_Cohorte' in perfil_idx.columns else ''
            riesgos_ext['Fecha_corte'] = riesgos_ext['estudiante_id'].map(perfil_idx['Fecha_corte']) if 'Fecha_corte' in perfil_idx.columns else ''
        riesgos_ext.to_csv('export/riesgos_externos_individual.csv', index=False)
        print('Exportado: export/riesgos_externos_individual.csv')

    # Exportar análisis BEG e ISPG con trazabilidad y resultados de análisis
    # Exportar solo un archivo de análisis global (EG_ANALISIS.csv) con todos los datos y análisis
    # Usar la lógica moderna de resumen y análisis
    # (Este bloque debe estar después de calcular el resumen de cohortes y riesgos)
    resumen_final_path = 'export/BEG_ISPG_M.csv'
    if 'resumen_df_final' in locals():
        resumen_df_final.to_csv(resumen_final_path, index=False)
        print(f'Exportado: {resumen_final_path}')
    # =====================
    # Exportación tradicional
    # =====================
    export_engine = ExportEngine(export_dir)
    export_engine.export(riesgos_internos, f'riesgos_internos_{run_id}.csv')
    export_engine.export(riesgos_externos, f'riesgos_externos_{run_id}.csv')

    # Exportación avanzada para Power BI
    results = []
    from datetime import datetime
    # TODO: Ajustar periodo y cohorte según datos reales
    periodo = ''
    cohorte = ''
    version_modelo = config['version_modelo']
    timestamp_export = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # RA
    for idx, row in ra_data.iterrows():
        results.append({
            'indicador_id': f"RA{str(idx+1).zfill(2)}",
            'nivel_analitico': 'RA',
            'tipo_indicador': 'academico',
            'categoria': 'aprendizaje',
            'periodo': periodo,
            'cohorte': cohorte,
            'ID_EST': row.get('ID_EST', row.get('estudiante_id', 'NA')),
            'ID_COMP': row.get('ID_COMP', 'NA'),
            'ID_PERFIL': row.get('ID_PERFIL', row.get('perfil_id', 'NA')) if ('ID_PERFIL' in row or 'perfil_id' in row) else 'NA',
            'valor': row.get('valor_minimo', 'NA'),
            'fuente': 'ra_competencia.csv',
            'fuente_detallada': 'Registro ERP académico',
            'formula': 'Valor mínimo declarado para RA-Competencia',
            'timestamp_export': timestamp_export,
            'run_id': run_id,
            'version_modelo': version_modelo
        })
    # Competencias
    for comp_id, valor in competencia_results.items():
        results.append({
            'indicador_id': f"COMP{comp_id}",
            'nivel_analitico': 'COMP',
            'tipo_indicador': 'academico',
            'categoria': 'competencia',
            'periodo': periodo,
            'cohorte': cohorte,
            'ID_EST': 'NA',
            'ID_COMP': comp_id,
            'ID_PERFIL': 'NA',
            'valor': valor,
            'fuente': 'competencia_perfil.csv',
            'fuente_detallada': 'Declaración de ponderaciones RA en competencia',
            'formula': 'Suma ponderada de RA: sum(PESO_RA_EN_COMPETENCIA * valor_minimo)',
            'timestamp_export': timestamp_export,
            'run_id': run_id,
            'version_modelo': version_modelo
        })
    # Perfil
    for perfil_id, valor in perfil_results.items():
        results.append({
            'indicador_id': f"PERF{perfil_id}",
            'nivel_analitico': 'PERFIL',
            'tipo_indicador': 'academico',
            'categoria': 'perfil',
            'periodo': periodo,
            'cohorte': cohorte,
            'ID_EST': 'NA',
            'ID_COMP': 'NA',
            'ID_PERFIL': perfil_id,
            'valor': valor,
            'fuente': 'competencia_perfil.csv',
            'fuente_detallada': 'Declaración de ponderaciones de competencias en perfil',
            'formula': 'Suma ponderada de competencias: sum(peso * valor_competencia)',
            'timestamp_export': timestamp_export,
            'run_id': run_id,
            'version_modelo': version_modelo
        })
    # Riesgos internos
    for idx, row in riesgos_internos.iterrows():
        for col in ['desempeño', 'repitencia', 'deserción']:
            results.append({
                'indicador_id': f"RI{str(idx+1).zfill(2)}_{col}",
                'nivel_analitico': 'RIESGO_INT',
                'tipo_indicador': 'riesgo',
                'categoria': col,
                'periodo': periodo,
                'cohorte': cohorte,
                'ID_EST': row.get('ID_EST', row.get('estudiante_id', 'NA')),
                'ID_COMP': 'NA',
                'ID_PERFIL': 'NA',
                'valor': row.get(col, 'NA'),
                'fuente': 'riesgos_internos.csv',
                'fuente_detallada': 'Registros ERP académico',
                'formula': f'Valor directo de columna {col}',
                'timestamp_export': timestamp_export,
                'run_id': run_id,
                'version_modelo': version_modelo
            })
    # Riesgos externos
    for idx, row in riesgos_externos.iterrows():
        for col in ['empleabilidad', 'satisfacción']:
            results.append({
                'indicador_id': f"RE{str(idx+1).zfill(2)}_{col}",
                'nivel_analitico': 'RIESGO_EXT',
                'tipo_indicador': 'riesgo',
                'categoria': col,
                'periodo': periodo,
                'cohorte': cohorte,
                'ID_EST': row.get('ID_EST', row.get('estudiante_id', 'NA')),
                'ID_COMP': 'NA',
                'ID_PERFIL': 'NA',
                'valor': row.get(col, 'NA'),
                'fuente': 'riesgos_externos.csv',
                'fuente_detallada': 'Encuestas a empleadores',
                'formula': f'Valor directo de columna {col}',
                'timestamp_export': timestamp_export,
                'run_id': run_id,
                'version_modelo': version_modelo
            })
    # Exportar resultados avanzados
    # Exportar resultados avanzados sobrescribiendo siempre el mismo archivo
    export_advanced(results, export_dir, 'resultados_avanzados.csv')

    # Resultados
    print(f"run_id: {run_id}")
    print(f"Alpha Cronbach: {alpha}")
    # print(f"Sensibilidad: {sensibilidad}")
    # print(f"Monte Carlo: {montecarlo}")
    print(f"Perfil: {perfil_results}")
    # BEG e ISPG se calculan y exportan al final del pipeline


    # Exportar BEG_logro agrupado por ID_Cohorte usando perfil_logro_individual.csv
    perfil_logro_path = 'export/perfil_logro_individual.csv'
    if os.path.exists(perfil_logro_path):
        perfil_logro = pd.read_csv(perfil_logro_path)
        if 'ID_Cohorte' not in perfil_logro.columns:
            raise ValueError('El archivo perfil_logro_individual.csv debe contener la columna ID_Cohorte. Verifique la generación de cohortes.')
        perfil_logro['Logro_Perfil'] = pd.to_numeric(perfil_logro['Logro_Perfil'], errors='coerce')
        perfil_logro = perfil_logro.dropna(subset=['Logro_Perfil'])
        fecha_analisis = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        fuente_datos = perfil_logro_path
        fecha_carga = perfil_logro['Fecha_corte'].iloc[0] if 'Fecha_corte' in perfil_logro.columns else ''
        resumenes = []
        for cohorte, grupo in perfil_logro.groupby('ID_Cohorte'):
            N = len(grupo)
            # Determinar nivel de análisis: máximo nivel alcanzado por la cohorte
            # Usar matric para obtener el máximo nivel cursado por los estudiantes de la cohorte
            ests_cohorte = grupo['ID_EST'].unique()
            niveles_est = matric[matric['ID_EST'].isin(ests_cohorte)]['Nivel'].dropna().str.upper().unique().tolist()
            # Ordenar niveles según el plan de estudios
            niveles_orden = ['PRIMER','SEGUNDO','TERCERO','CUARTO','QUINTO','SEXTO','SEPTIMO','OCTAVO','NOVENO']
            nivel_analisis = ''
            for n in reversed(niveles_orden):
                if n in niveles_est:
                    nivel_analisis = n
                    break
            # BEG: solo estudiantes con logros en NOVENO nivel
            est_noveno = matric[(matric['ID_EST'].isin(ests_cohorte)) & (matric['Nivel'].str.upper() == 'NOVENO')]['ID_EST'].unique()
            grupo_noveno = grupo[grupo['ID_EST'].isin(est_noveno)]
            promedio_noveno = round(grupo_noveno['Logro_Perfil'].mean(), 2) if not grupo_noveno.empty else 0
            beg = round(100 - promedio_noveno, 2) if promedio_noveno else ''
            # PRE_BEG: estudiantes con logros en OCTAVO nivel
            est_octavo = matric[(matric['ID_EST'].isin(ests_cohorte)) & (matric['Nivel'].str.upper() == 'OCTAVO')]['ID_EST'].unique()
            grupo_octavo = grupo[grupo['ID_EST'].isin(est_octavo)]
            promedio_octavo = round(grupo_octavo['Logro_Perfil'].mean(), 2) if not grupo_octavo.empty else 0
            pre_beg = round(100 - promedio_octavo, 2) if promedio_octavo else ''
            resumenes.append({
                'ID_Cohorte': cohorte,
                'N': N,
                'Nivel_Analisis': nivel_analisis,
                'Promedio_Logro_Perfil_Noveno': promedio_noveno,
                'BEG': beg,
                'PRE_BEG': pre_beg,
                'Fuente_datos': fuente_datos,
                'Fecha_carga': fecha_carga,
                'Fecha_analisis': fecha_analisis
            })
        if resumenes:
            resumen_df = pd.DataFrame(resumenes)
            # Calcular y exportar BEG_ISPG_analisis.csv directamente
            try:
                riesgos_int = pd.read_csv('export/riesgos_internos_individual.csv')
                riesgos_ext_path = os.path.join('ssd_core', 'config', 'riesgos_externos.csv')
                print(f"[DEBUG] Usando archivo de riesgos externos: {riesgos_ext_path}")
                if not os.path.exists(riesgos_ext_path):
                    print(f"[ERROR] No se encontró el archivo de riesgos externos esperado: {riesgos_ext_path}")
                riesgos_ext = pd.read_csv(riesgos_ext_path)
                est_to_cohorte = perfil_logro.set_index('ID_EST')['ID_Cohorte'].to_dict() if 'ID_EST' in perfil_logro.columns else {}
                riesgos_int['ID_Cohorte'] = riesgos_int['ID_EST'].map(est_to_cohorte) if 'ID_EST' in riesgos_int.columns and est_to_cohorte else None
                riesgos_ext['ID_Cohorte'] = riesgos_ext['estudiante_id'].map(est_to_cohorte) if 'estudiante_id' in riesgos_ext.columns and est_to_cohorte else None
                if 'desempeño' in riesgos_int.columns:
                    riesgos_int['riesgo_interno'] = riesgos_int[['desempeño','repitencia','deserción']].mean(axis=1)
                if 'empleabilidad' in riesgos_ext.columns:
                    riesgos_ext['riesgo_externo'] = riesgos_ext[['empleabilidad','satisfacción']].mean(axis=1)
                # Calcular riesgo externo global: mediana de los riesgos externos de los estudiantes de las cohortes de los últimos 5 años
                cohortes_ordenadas = sorted(resumen_df['ID_Cohorte'].unique(), reverse=True)
                cohortes_ultimos_5 = cohortes_ordenadas[:5]
                valores_ultimos_5 = riesgos_ext[riesgos_ext['ID_Cohorte'].isin(cohortes_ultimos_5)]['riesgo_externo'] if 'riesgo_externo' in riesgos_ext.columns else []
                if len(valores_ultimos_5) > 0:
                    riesgo_ext_global = float(np.median(valores_ultimos_5))
                else:
                    riesgo_ext_global = 0
                riesgo_int_cohorte = riesgos_int.groupby('ID_Cohorte')['riesgo_interno'].mean()
                resumenes_final = []
                for idx, row in resumen_df.iterrows():
                    cohorte = row['ID_Cohorte']
                    beg = row['BEG']/100 if row['BEG'] > 1 else row['BEG']
                    riesgo_int = riesgo_int_cohorte.get(cohorte, 0)
                    riesgo_ext = riesgo_ext_global
                    ispg = 0.50*beg - 0.30*riesgo_int - 0.20*riesgo_ext
                    ispg_norm = max(0, min(1, ispg))
                    if ispg_norm >= 0.75:
                        clasificacion = 'Verde'
                    elif ispg_norm >= 0.60:
                        clasificacion = 'Amarillo'
                    else:
                        clasificacion = 'Rojo'
                    resumenes_final.append({
                        'ID_Cohorte': cohorte,
                        'N': row['N'],
                        'Nivel_Analisis': row['Nivel_Analisis'],
                        'Promedio_Logro_Perfil_Noveno': row['Promedio_Logro_Perfil_Noveno'],
                        'BEG': row['BEG'],
                        'PRE_BEG': row['PRE_BEG'],
                        'Riesgo_interno': round(riesgo_int,3),
                        'Riesgo_externo': round(riesgo_ext,3),
                        'ISPG': round(ispg,3),
                        'ISPG_norm': round(ispg_norm,3),
                        'Clasificacion': clasificacion,
                        'Fuente_datos': row['Fuente_datos'],
                        'Fecha_carga': row['Fecha_carga'],
                        'Fecha_analisis': row['Fecha_analisis'],
                        'Alpha_Cronbach': alpha if alpha is not None else '',
                        'MonteCarlo_mean': montecarlo['montecarlo_mean'] if montecarlo and 'montecarlo_mean' in montecarlo else '',
                        'MonteCarlo_std': montecarlo['montecarlo_std'] if montecarlo and 'montecarlo_std' in montecarlo else ''
                    })
                if resumenes_final:
                    resumen_df_final = pd.DataFrame(resumenes_final)
                    resumen_df_final.to_csv('export/BEG_ISPG_M.csv', index=False)
                    print('Exportado: export/BEG_ISPG_M.csv')
                else:
                    print('No hay cohortes válidas para análisis en BEG_ISPG_M.')
            except Exception as e:
                print(f'Error al calcular/exportar BEG_ISPG_analisis: {e}')
        else:
            print('No hay datos numéricos válidos en Logro_Perfil para calcular BEG_ISPG_analisis.')
    else:
        print('No se encontró el archivo export/perfil_logro_individual.csv para exportar BEG_ISPG_analisis.')

if __name__ == "__main__":
    main(carrera_id=101)