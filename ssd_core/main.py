# main.py
# Orquestador principal del SSD Curricular
import os
from base.config_loader import ConfigLoader
from base.data_loader import DataLoader
from base.audit_trail import AuditTrail
from base.ssd_runner import SSDRunner
from engines.ra_engine import RAEngine
from engines.competencia_engine import CompetenciaEngine
from engines.perfil_engine import PerfilEngine
from engines.external_risk_engine import ExternalRiskEngine
from engines.internal_risk_engine import InternalRiskEngine
from engines.beg_engine import BEGEngine
from engines.ispg_engine import ISPGEngine
from engines.normalizacion_engine import NormalizacionEngine
from validation.cronbach import CronbachValidator
from validation.sensibilidad import SensibilidadValidator
from validation.montecarlo import MonteCarloValidator
from export.powerbi_export import ExportEngine

def main(carrera_id):
    # Paths
    config_path = os.path.join('config', 'model_config.yaml')
    ra_path = os.path.join('config', 'ra_competencia.csv')
    competencia_path = os.path.join('config', 'competencia_perfil.csv')
    perfil_path = os.path.join('config', 'competencia_perfil.csv')
    riesgos_internos_path = os.path.join('config', 'riesgos_internos.csv')
    riesgos_externos_path = os.path.join('config', 'riesgos_externos.csv')
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

    # Exportación
    export_engine = ExportEngine(export_dir)
    export_engine.export(ra_data, f'ra_output_{run_id}.csv')
    export_engine.export(riesgos_internos, f'riesgos_internos_{run_id}.csv')
    export_engine.export(riesgos_externos, f'riesgos_externos_{run_id}.csv')

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