# main.py
# Orquestador principal del SSD Curricular
import os
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
    competencia_data = DataLoader(competencia_path).load()
    perfil_data = DataLoader(perfil_path).load()
    riesgos_internos = DataLoader(riesgos_internos_path).load()
    riesgos_externos = DataLoader(riesgos_externos_path).load()

    # Engines
    ra_engine = RAEngine(ra_data)
    competencia_engine = CompetenciaEngine(competencia_data, ra_data)
    competencia_results = competencia_engine.calculate(student_id=None)
    perfil_engine = PerfilEngine(perfil_data, competencia_results)
    perfil_results = perfil_engine.calculate()
    external_risk_engine = ExternalRiskEngine(riesgos_externos)
    internal_risk_engine = InternalRiskEngine(riesgos_internos)
    beg_engine = BEGEngine(ra_data)
    ispg_engine = ISPGEngine(ra_data)
    normalizacion_engine = NormalizacionEngine(ra_data)

    # Validaciones
    cronbach_validator = CronbachValidator(ra_data)
    alpha = cronbach_validator.calculate_alpha()
    sensibilidad_validator = SensibilidadValidator(ra_data)
    sensibilidad = sensibilidad_validator.analyze()
    montecarlo_validator = MonteCarloValidator(ra_data)
    montecarlo = montecarlo_validator.simulate()

    # Auditoría
    audit_trail = AuditTrail(audit_dir)
    config_hash = audit_trail.hash_file(config_path)
    data_hash = audit_trail.hash_file(ra_path)
    run_id = audit_trail.register(config_hash, data_hash, carrera_id, config['version_modelo'])


    # Exportación tradicional
    export_engine = ExportEngine(export_dir)
    export_engine.export(riesgos_internos, f'riesgos_internos_{run_id}.csv')
    export_engine.export(riesgos_externos, f'riesgos_externos_{run_id}.csv')

    # Exportación avanzada para Power BI
    results = []
    from datetime import datetime
    periodo = 'O2025-1'  # Ejemplo, ajustar según datos reales
    cohorte = '2025'     # Ejemplo, ajustar según datos reales
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
            'ID_COMP': row.get('ID_COMP', row.get('competencia_id', 'NA')) if ('ID_COMP' in row or 'competencia_id' in row) else 'NA',
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
    export_advanced(results, export_dir, f'resultados_avanzados_{run_id}.csv')

    # Resultados
    print(f"run_id: {run_id}")
    print(f"Alpha Cronbach: {alpha}")
    print(f"Sensibilidad: {sensibilidad}")
    print(f"Monte Carlo: {montecarlo}")
    print(f"Perfil: {perfil_results}")
    print(f"BEG: {beg_engine.calculate()}")
    print(f"ISPG: {ispg_engine.calculate()}")

if __name__ == "__main__":
    main(carrera_id=101)