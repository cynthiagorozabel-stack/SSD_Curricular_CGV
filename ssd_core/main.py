# main.py
import os
import pandas as pd
import numpy as np
from ssd_core.base.config_loader import ConfigLoader
from ssd_core.base.data_loader import DataLoader
from ssd_core.base.audit_trail import AuditTrail
from ssd_core.base.ssd_runner import SSDRunner
from ssd_core.engines.ra_engine import RAEngine
from ssd_core.engines.competencia_engine import CompetenciaEngine
from ssd_core.engines.perfil_engine import PerfilEngine
from ssd_core.engines.external_risk_engine import ExternalRiskEngine
from ssd_core.engines.internal_risk_engine import InternalRiskEngine
from ssd_core.validation.cronbach import CronbachValidator
from ssd_core.validation.sensibilidad import SensibilidadValidator
from ssd_core.validation.montecarlo import MonteCarloValidator
from ssd_core.export.powerbi_export import ExportEngine
from ssd_core.export.advanced_export import export_advanced

def main(carrera_id):
    import time
    start_time = time.time()
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
    # Homologar ra_id a RA_ID
    if 'ra_id' in ra_data.columns:
        ra_data = ra_data.rename(columns={'ra_id': 'RA_ID'})
    # Homologar RA_ID a ID_RA para compatibilidad con engines
    if 'RA_ID' in ra_data.columns:
        ra_data = ra_data.rename(columns={'RA_ID': 'ID_RA'})
    # Homologar competencia_id a ID_COMP si existiera
    if 'competencia_id' in ra_data.columns:
        ra_data = ra_data.rename(columns={'competencia_id': 'ID_COMP'})
    # Homologar y mapear COD_ASIGNATURA a cada RA_ID usando asignaturas.csv
    asig_path = os.path.join('ssd_core', 'config', 'asignaturas.csv')
    asig_data = pd.read_csv(asig_path)
    ra_to_asig = asig_data.set_index('RA')['COD_ASIGNATURA'].to_dict() if 'RA' in asig_data.columns and 'COD_ASIGNATURA' in asig_data.columns else {}
    if 'RA_ID' in ra_data.columns and ra_to_asig:
        ra_data['COD_ASIGNATURA'] = ra_data['RA_ID'].map(ra_to_asig)
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
    # (BEG, ISPG y normalizacion_engine removidos para futura implementación desde cero)

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
    # import numpy as np  # Eliminado, ya está importado globalmente
    # Cargar datos necesarios
    # Leer solo columnas necesarias, excluyendo ID_carrera
    usecols = ['Periodo','Fecha_matriculacion','Fecha_carga','ID_EST','Nivel','COD_ASIGNATURA','Nota','ID_Cohorte','Abandono']
    matric = pd.read_csv('ssd_core/config/matriculacion_historica_test.csv', usecols=usecols)
    # Asegurar que la columna de nivel esté en mayúsculas para compatibilidad
    if 'Nivel' in matric.columns and 'NIVEL' not in matric.columns:
        matric = matric.rename(columns={'Nivel': 'NIVEL'})
    asig = pd.read_csv('ssd_core/config/asignaturas.csv')
    comp_perfil = pd.read_csv('ssd_core/config/competencia_perfil.csv')
    # Homologar columnas de ID y asignaturas
    matric = matric.rename(columns={'Estudiante_ID':'ID_EST', 'Materia':'COD_ASIGNATURA'})
    comp_perfil = comp_perfil.rename(columns={'competencia_id': 'ID_COMP'})
    # Mapear materias a RA
    materia_ra = asig.set_index('COD_ASIGNATURA')['RA'].to_dict()
    matric['RA'] = matric['COD_ASIGNATURA'].map(materia_ra)
    # Filtrar solo filas con RA válido y nota numérica
    matric = matric[matric['RA'].notnull() & matric['Nota'].apply(lambda x: str(x).replace('.','',1).isdigit())]
    matric['Nota'] = matric['Nota'].astype(float)
    # Ordenar por ID_EST, RA, Periodo (de mayor a menor) para deduplicar repitencias
    matric = matric.sort_values(['ID_EST', 'RA', 'Periodo'], ascending=[True, True, False])
    # Dejar solo la última nota por RA y estudiante
    matric_clean = matric.drop_duplicates(['ID_EST', 'RA'], keep='first')
    # Calcular nivel de logro por estudiante y RA (ya solo hay una nota por RA)
    # Mapear el nivel real de la asignatura asociada a cada RA
    ra_nivel_map = asig.drop_duplicates('RA').set_index('RA')['NIVEL'].to_dict()
    ra_logro = matric_clean[['ID_EST', 'RA', 'Nota']].rename(columns={'Nota': 'Logro_RA'})
    ra_logro['Fecha_corte'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    # Agregar ID_Cohorte y Nivel real de la asignatura a ra_logro
    id_cohorte_map = matric.drop_duplicates('ID_EST').set_index('ID_EST')['ID_Cohorte'].to_dict()
    ra_logro['ID_Cohorte'] = ra_logro['ID_EST'].map(id_cohorte_map)
    ra_logro['Nivel'] = ra_logro['RA'].map(ra_nivel_map)
    # Calcular logro de competencia por estudiante
    comp_logro = []
    nivel_order = {
        'PRIMER': 1, 'SEGUNDO': 2, 'TERCERO': 3, 'CUARTO': 4, 'QUINTO': 5, 'SEXTO': 6, 'SEPTIMO': 7, 'OCTAVO': 8, 'NOVENO': 9
    }
    for est in ra_logro['ID_EST'].unique():
        est_ra = ra_logro[ra_logro['ID_EST']==est]
        for comp in comp_perfil['ID_COMP'].unique():
            # Buscar todos los RA asociados a esta competencia
            ra_asociados = asig[(asig['RA'].notnull()) & (asig['RA'].str.startswith('RA')) & (asig['RA'].isin(est_ra['RA']))]['RA'].unique().tolist()
            ra_vals = est_ra[est_ra['RA'].isin(ra_asociados)]['Logro_RA']
            # Nivel real: máximo nivel de los RA asociados a la competencia para este estudiante
            niveles_ra = est_ra[est_ra['RA'].isin(ra_asociados)]['RA'].map(ra_nivel_map).dropna().tolist()
            nivel_real = ''
            if niveles_ra:
                nivel_real = max(niveles_ra, key=lambda x: nivel_order.get(x, 0))
            if not ra_vals.empty:
                comp_logro.append({'ID_EST':est, 'ID_COMP':comp, 'Logro_Competencia':ra_vals.mean(), 'Fecha_corte':pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'), 'ID_Cohorte': id_cohorte_map.get(est, ''), 'Nivel': nivel_real})
    comp_logro = pd.DataFrame(comp_logro)
    # Calcular perfil por estudiante y periodo (suma ponderada de competencias)
    # Extraer nivel y periodo desde matriculacion_historica_test.csv
    perfil_logro = []
    for (est, periodo), grupo_m in matric.groupby(['ID_EST', 'Periodo']):
        # Nivel real: máximo nivel de las asignaturas cursadas en ese periodo
        niveles_periodo = grupo_m['NIVEL'].dropna().tolist() if 'NIVEL' in grupo_m.columns else []
        nivel_real = ''
        if niveles_periodo:
            # Usar el nivel más alto realmente cursado por el estudiante en ese periodo
            niveles_validos = [n for n in niveles_periodo if n in nivel_order]
            if niveles_validos:
                nivel_real = max(niveles_validos, key=lambda x: nivel_order[x])
        id_cohorte = grupo_m['ID_Cohorte'].iloc[0] if 'ID_Cohorte' in grupo_m.columns else ''
        # Calcular logros de competencia para este estudiante y periodo
        est_comp = comp_logro[comp_logro['ID_EST'] == est]
        for perfil in comp_perfil['perfil_id'].unique():
            compas = comp_perfil[comp_perfil['perfil_id'] == perfil]['ID_COMP']
            vals = est_comp[est_comp['ID_COMP'].isin(compas)]['Logro_Competencia']
            if not vals.empty:
                perfil_logro.append({
                    'ID_EST': est,
                    'ID_PERFIL': perfil,
                    'Periodo': periodo,
                    'Nivel': nivel_real,
                    'ID_Cohorte': id_cohorte,
                    'Logro_Perfil': vals.mean(),
                    'Fecha_corte': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                })
    perfil_logro = pd.DataFrame(perfil_logro)

    # Calcular PERFIL_Promedio único por estudiante: solo el último periodo y nivel más alto
    if not perfil_logro.empty:
        # Tomar solo el último periodo por estudiante
        perfil_logro['Periodo_orden'] = perfil_logro['Periodo'].astype(str)
        perfil_logro = perfil_logro.sort_values(['ID_EST', 'Periodo_orden'])
        last_period = perfil_logro.groupby('ID_EST')['Periodo_orden'].transform('max')
        perfil_logro_last = perfil_logro[perfil_logro['Periodo_orden'] == last_period]
        # Definir el orden de los niveles
        nivel_order = {
            'PRIMER': 1,
            'SEGUNDO': 2,
            'TERCERO': 3,
            'CUARTO': 4,
            'QUINTO': 5,
            'SEXTO': 6,
            'SEPTIMO': 7,
            'OCTAVO': 8,
            'NOVENO': 9
        }
        def nivel_mas_alto(niveles):
            niveles_validos = [n for n in niveles if n in nivel_order]
            if not niveles_validos:
                return ''
            return max(niveles_validos, key=lambda x: nivel_order[x])
        # Calcular el promedio de Logro_Perfil en el último periodo y el nivel más alto
        perfil_promedio = perfil_logro_last.groupby('ID_EST').agg({
            'Logro_Perfil': 'mean',
            'Nivel': nivel_mas_alto,
            'ID_Cohorte': 'first',
            'Periodo': 'first',
            'Fecha_corte': 'first'
        }).reset_index().rename(columns={'Logro_Perfil': 'PERFIL_Promedio'})
    else:
        perfil_promedio = pd.DataFrame()
    # Calcular riesgos internos individuales solo para datos de los últimos dos años
    from datetime import datetime, timedelta
    def safe_float(x):
        try:
            return float(x)
        except:
            return np.nan
    # Convertir Fecha_carga a datetime
    if 'Fecha_carga' in matric.columns:
        matric['Fecha_carga_dt'] = pd.to_datetime(matric['Fecha_carga'], errors='coerce')
        fecha_max = matric['Fecha_carga_dt'].max()
        if pd.notnull(fecha_max):
            fecha_limite = fecha_max - pd.DateOffset(years=2)
            matric = matric[matric['Fecha_carga_dt'] >= fecha_limite]
    matric['Nota_num'] = matric['Nota'].apply(safe_float)
    riesgos_calc = []
    for est, grupo in matric.groupby('ID_EST'):
        notas_validas = grupo['Nota_num'].dropna()
        desempeno = notas_validas.mean() if not notas_validas.empty else np.nan
        repitencia = grupo.groupby('COD_ASIGNATURA').size()
        repitencia = (repitencia > 1).sum()
        desercion = grupo['Abandono'].fillna(0).astype(int).sum()
        riesgos_calc.append({'ID_EST': est, 'desempeño': round(desempeno,2) if not np.isnan(desempeno) else '', 'repitencia': repitencia, 'deserción': desercion})
    riesgos_int_export = pd.DataFrame(riesgos_calc)
    # Exportar archivos
    # Exportar ra_logro_individual con ID_Cohorte
    # Mapear RA a RA_ID usando ra_data si existe
    ra_id_map = None
    if 'RA_ID' in ra_data.columns and 'RA' in ra_data.columns:
        ra_id_map = ra_data.drop_duplicates('RA')[['RA', 'RA_ID']].set_index('RA')['RA_ID'].to_dict()
    ra_logro['RA_ID'] = ra_logro['RA'].map(ra_id_map) if ra_id_map else ra_logro['RA']
    ra_cols = ['ID_EST', 'RA_ID', 'RA', 'Logro_RA', 'Fecha_corte', 'ID_Cohorte', 'Nivel']
    ra_export = ra_logro[ra_cols] if all(col in ra_logro.columns for col in ra_cols) else ra_logro
    ra_export.to_csv('export/ra_logro_individual.csv', index=False)

    # Exportar competencia_logro_individual con ID_Cohorte
    comp_cols = ['ID_EST', 'ID_COMP', 'Logro_Competencia', 'Fecha_corte', 'ID_Cohorte', 'Nivel']
    comp_export = comp_logro[comp_cols] if all(col in comp_logro.columns for col in comp_cols) else comp_logro
    comp_export.to_csv('export/competencia_logro_individual.csv', index=False)
    perfil_logro.to_csv('export/perfil_logro_individual.csv', index=False)
    if not perfil_promedio.empty:
        perfil_promedio_path = os.path.join(export_dir, 'perfil_promedio_individual.csv')
        perfil_promedio.to_csv(perfil_promedio_path, index=False)
        # === Exportar perfil promedio de egresados por cohorte ===
        # Parametrizar el nivel máximo de la carrera desde config
        NIVEL_MAXIMO = config.get('nivel_maximo_egreso', 'NOVENO')
        if NIVEL_MAXIMO is None:
            NIVEL_MAXIMO = 'NOVENO'
        egresados = perfil_promedio[perfil_promedio['Nivel'] == NIVEL_MAXIMO].copy()
        if not egresados.empty:
            perfil_egresados_cohorte = egresados.groupby(['ID_Cohorte', 'Periodo']).agg({
                'PERFIL_Promedio': 'mean',
                'Fecha_corte': 'last'
            }).reset_index().rename(columns={'PERFIL_Promedio': 'Perfil_Promedio_Cohorte'})
            perfil_egresados_cohorte['Fecha_generacion_indicador'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            perfil_egresados_cohorte['Fuente_datos'] = perfil_promedio_path
            perfil_egresados_cohorte['Nivel_maximo'] = NIVEL_MAXIMO
            perfil_egresados_cohorte_path = os.path.join(export_dir, 'perfil_promedio_egresados_cohorte.csv')
            perfil_egresados_cohorte.to_csv(perfil_egresados_cohorte_path, index=False)
        else:
            perfil_egresados_cohorte_path = None
    else:
        perfil_promedio_path = None
        perfil_egresados_cohorte_path = None
    # Sobrescribir riesgos internos individuales siempre
    # Añadir trazabilidad a riesgos internos: ID_Cohorte, Nivel, Periodo, Fecha_matriculacion, Fecha_carga desde matric
    id_cohorte_map = matric.drop_duplicates('ID_EST').set_index('ID_EST')['ID_Cohorte'].to_dict() if 'ID_Cohorte' in matric.columns else {}
    nivel_map = matric.drop_duplicates('ID_EST').set_index('ID_EST')['Nivel'].to_dict() if 'Nivel' in matric.columns else {}
    periodo_map = matric.drop_duplicates('ID_EST').set_index('ID_EST')['Periodo'].to_dict() if 'Periodo' in matric.columns else {}
    fecha_mat_map = matric.drop_duplicates('ID_EST').set_index('ID_EST')['Fecha_matriculacion'].to_dict() if 'Fecha_matriculacion' in matric.columns else {}
    fecha_carga_map = matric.drop_duplicates('ID_EST').set_index('ID_EST')['Fecha_carga'].to_dict() if 'Fecha_carga' in matric.columns else {}
    riesgos_int_export['ID_Cohorte'] = riesgos_int_export['ID_EST'].map(id_cohorte_map) if id_cohorte_map else ''
    # Asignar el nivel real máximo alcanzado por cada estudiante
    nivel_order = {
        'PRIMER': 1, 'SEGUNDO': 2, 'TERCERO': 3, 'CUARTO': 4, 'QUINTO': 5, 'SEXTO': 6, 'SEPTIMO': 7, 'OCTAVO': 8, 'NOVENO': 9
    }
    if 'NIVEL' in matric.columns:
        nivel_map_real = matric.groupby('ID_EST')['NIVEL'].apply(lambda x: max(x, key=lambda y: nivel_order.get(y, 0))).to_dict()
        riesgos_int_export['Nivel'] = riesgos_int_export['ID_EST'].map(nivel_map_real)
    else:
        riesgos_int_export['Nivel'] = ''
    riesgos_int_export['Periodo'] = riesgos_int_export['ID_EST'].map(periodo_map) if periodo_map else ''
    riesgos_int_export['Fecha_matriculacion'] = riesgos_int_export['ID_EST'].map(fecha_mat_map) if fecha_mat_map else ''
    riesgos_int_export['Fecha_carga'] = riesgos_int_export['ID_EST'].map(fecha_carga_map) if fecha_carga_map else ''
    riesgos_internos_path_export = os.path.join(export_dir, 'riesgos_internos_individual.csv')
    riesgos_int_export.to_csv(riesgos_internos_path_export, index=False)
    print('Exportados: ra_logro_individual.csv, competencia_logro_individual.csv, perfil_logro_individual.csv, riesgos_internos_individual.csv')

    # Exportar riesgos externos individuales si existe
    riesgos_ext_export_path = os.path.join(export_dir, 'riesgos_externos_individual.csv')
    if os.path.exists(riesgos_ext_export_path):
        riesgos_externos_path_export = riesgos_ext_export_path
    else:
        riesgos_externos_path_export = None

    # =====================
    # Calcular y exportar BEG (por cohorte de egresados)
    # =====================
    from ssd_core.engines.beg_engine import BEGEngine
    beg_export_path = os.path.join(export_dir, 'beg_cohorte.csv')
    if perfil_egresados_cohorte_path and os.path.exists(perfil_egresados_cohorte_path):
        beg_engine = BEGEngine(perfil_egresados_cohorte_path, config_path)
        beg_engine.exportar_beg(beg_export_path)
        print(f"Exportado: {beg_export_path}")
    else:
        beg_export_path = None

    # =====================
    # Exportar matriz de logros individuales y riesgos externos individuales
    # =====================
        # =====================
        # Calcular y exportar ISPG (debe ir al final, tras exportar todos los archivos intermedios)
        # =====================
        from ssd_core.engines.ispg_engine import ISPGEngine
        ispg_export_path = os.path.join(export_dir, 'ispg_individual.csv')
        # Usar riesgos_externos_individual.csv para ISPG
        riesgos_externos_individual_path = os.path.join(export_dir, 'riesgos_externos_individual.csv')
        # Renombrar columna estudiante_id a ID_EST si es necesario
        # Verificar existencia física de los archivos requeridos
        if all(os.path.exists(p) for p in [beg_export_path, riesgos_internos_path_export, riesgos_externos_individual_path]):
            df_re = pd.read_csv(riesgos_externos_individual_path)
            if 'estudiante_id' in df_re.columns:
                df_re = df_re.rename(columns={'estudiante_id': 'ID_EST'})
                df_re.to_csv(riesgos_externos_individual_path, index=False)
            ispg_engine = ISPGEngine(beg_export_path, riesgos_internos_path_export, riesgos_externos_individual_path)
            ispg_engine.exportar_ispg(ispg_export_path)
            print(f"Exportado: {ispg_export_path}")
        else:
            print("[WARN] No se pudo calcular ISPG por falta de archivos exportados requeridos.")
    # Matriz de logros RA (estudiante x RA)
    ra_matrix = ra_logro.pivot(index='ID_EST', columns='RA', values='Logro_RA')
    # Agregar desempeño, repitencia, deserción, perfil, periodo, fechas
    # Desempeño, repitencia, deserción ya calculados en riesgos_int_export
    perfil_logro_idx = perfil_logro.set_index('ID_EST') if 'ID_EST' in perfil_logro.columns else pd.DataFrame()
    # Unir todo por estudiante y periodo

    full_matrix = None
    if not perfil_promedio.empty:
        # Merge ra_matrix con perfil_promedio para tener PERFIL_Promedio, Nivel, Periodo, etc.
        ra_matrix_reset = ra_matrix.reset_index()
        # Expand ra_matrix para cada periodo del estudiante
        ra_matrix_expanded = ra_matrix_reset.merge(perfil_promedio[['ID_EST','Periodo','PERFIL_Promedio','Nivel','ID_Cohorte','Fecha_corte']], on='ID_EST', how='right')
        # Agregar desempeño, repitencia, deserción
        for col in ['desempeño','repitencia','deserción']:
            if col in riesgos_int_export.set_index('ID_EST').columns:
                ra_matrix_expanded[col] = ra_matrix_expanded['ID_EST'].map(riesgos_int_export.set_index('ID_EST')[col])
        # Agregar columnas de logros por competencia para cada estudiante
        if not comp_logro.empty:
            comp_matrix = comp_logro.pivot(index='ID_EST', columns='ID_COMP', values='Logro_Competencia')
            comp_matrix.columns = [f'COMP_{col}' for col in comp_matrix.columns]
            ra_matrix_expanded = ra_matrix_expanded.join(comp_matrix, on='ID_EST', how='left')
        # Exportar
        ra_matrix_expanded.to_csv('export/ra_logro_matrix.csv', index=False)
        print('Exportado: export/ra_logro_matrix.csv')
        full_matrix = ra_matrix_expanded.copy()
    else:
        # Fallback a lógica anterior si no hay perfil_promedio
        full_matrix = ra_matrix.copy()
        for col in ['desempeño','repitencia','deserción']:
            if col in riesgos_int_export.set_index('ID_EST').columns:
                full_matrix[col] = riesgos_int_export.set_index('ID_EST')[col]
        if 'Logro_Perfil' in perfil_logro_idx.columns:
            full_matrix['Logro_Perfil'] = perfil_logro_idx['Logro_Perfil']
        if 'ID_PERFIL' in perfil_logro_idx.columns:
            full_matrix['ID_PERFIL'] = perfil_logro_idx['ID_PERFIL']
        if not comp_logro.empty:
            comp_matrix = comp_logro.pivot(index='ID_EST', columns='ID_COMP', values='Logro_Competencia')
            comp_matrix.columns = [f'COMP_{col}' for col in comp_matrix.columns]
            full_matrix = full_matrix.join(comp_matrix, how='left')
        if 'Fecha_corte' in perfil_logro_idx.columns:
            full_matrix['Fecha_corte'] = perfil_logro_idx['Fecha_corte']
        full_matrix = full_matrix.reset_index()
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

    # =====================
    # Exportar riesgos externos individuales (estudiante x riesgo) con trazabilidad
    # Solo exportar riesgos_externos_individual.csv con columnas trazables
    if 'riesgos_ext' not in locals():
        # Si no existe, crear desde riesgos_externos
        riesgos_ext = riesgos_externos.copy()
    # Añadir trazabilidad a riesgos externos: ID_Cohorte y Fecha_corte usando perfil_promedio
    if not perfil_promedio.empty and 'estudiante_id' in riesgos_ext.columns:
        perfil_idx = perfil_promedio.set_index('ID_EST')
        riesgos_ext['ID_Cohorte'] = riesgos_ext['estudiante_id'].map(perfil_idx['ID_Cohorte']) if 'ID_Cohorte' in perfil_idx.columns else ''
        riesgos_ext['Fecha_corte'] = riesgos_ext['estudiante_id'].map(perfil_idx['Fecha_corte']) if 'Fecha_corte' in perfil_idx.columns else ''
    # Homologar columna ID_EST
    if 'estudiante_id' in riesgos_ext.columns:
        riesgos_ext = riesgos_ext.rename(columns={'estudiante_id': 'ID_EST'})
    riesgos_ext.to_csv('export/riesgos_externos_individual.csv', index=False)
    print('Exportado: export/riesgos_externos_individual.csv')

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

    # === CHECKLIST DE VALIDACIÓN ===
    elapsed = (time.time() - start_time) * 1000  # ms
    print("\n=== CHECKLIST DE VALIDACIÓN SSD ===")
    # 1. Datos completos
    try:
        n_estudiantes = len(set(ra_logro['ID_EST']))
        n_logros = len(ra_logro)
        n_periodos = len(set(matric['Periodo']))
        print(f"[✓] DATOS COMPLETOS: {n_estudiantes} estudiantes, {n_logros} logros, {n_periodos} períodos")
    except Exception as e:
        print(f"[✗] DATOS COMPLETOS: Error ({e})")
    # 2. Integridad (FKs)
    try:
        orphan_ra = ra_logro[~ra_logro['RA'].isin(asig['RA'])]
        if orphan_ra.empty:
            print("[✓] INTEGRIDAD: Todas las FKs válidas, sin datos huérfanos")
        else:
            print(f"[✗] INTEGRIDAD: {len(orphan_ra)} datos huérfanos en RA")
    except Exception as e:
        print(f"[✗] INTEGRIDAD: Error ({e})")
    # 3. Rango [0,1]
    try:
        rango_ok = ra_logro['Logro_RA'].between(0,1).all()
        if rango_ok:
            print("[✓] RANGO: Todos los valores en [0,1]")
        else:
            print("[✗] RANGO: Hay valores fuera de [0,1]")
    except Exception as e:
        print(f"[✗] RANGO: Error ({e})")
    # 4. Convergencia (tiempo)
    print(f"[{'✓' if elapsed <= 500 else '✗'}] CONVERGENCIA: Pipeline ejecuta en {elapsed:.0f} ms")
    # 5. Resultado ISPG
    try:
        ispg_path = 'export/ispg_individual.csv'
        if os.path.exists(ispg_path):
            ispg_df = pd.read_csv(ispg_path)
            ispg_ok = ispg_df['ISPG_norm'].between(0,1).all()
            clasif_ok = ispg_df['clasificacion'].isin(['Rojo','Amarillo','Verde']).all()
            if ispg_ok and clasif_ok:
                print("[✓] RESULTADO: ISPG entre [0,1], clasificación válida (Rojo/Amarillo/Verde)")
            else:
                print("[✗] RESULTADO: ISPG fuera de rango o clasificación inválida")
        else:
            print("[✗] RESULTADO: No se encontró archivo ISPG")
    except Exception as e:
        print(f"[✗] RESULTADO: Error ({e})")
    # 6. Output
    try:
        outputs = [
            'export/ra_logro_individual.csv',
            'export/competencia_logro_individual.csv',
            'export/perfil_logro_individual.csv',
            'export/riesgos_internos_individual.csv',
            'export/ispg_individual.csv'
        ]
        missing = [f for f in outputs if not os.path.exists(f)]
        if not missing:
            print("[✓] OUTPUT: Archivos generados sin errores")
        else:
            print(f"[✗] OUTPUT: Faltan archivos: {', '.join(missing)}")
    except Exception as e:
        print(f"[✗] OUTPUT: Error ({e})")

if __name__ == "__main__":
    main(carrera_id=101)