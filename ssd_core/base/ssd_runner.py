# ssd_runner.py
# Orquestador principal del SSD Curricular
from .config_loader import ConfigLoader
from .data_loader import DataLoader
from .audit_trail import AuditTrail

class SSDRunner:
    def __init__(self, config_path, data_path, audit_dir):
        self.config_loader = ConfigLoader(config_path)
        self.data_loader = DataLoader(data_path)
        self.audit_trail = AuditTrail(audit_dir)

    def run(self, carrera_id):
        config = self.config_loader.load()
        self.config_loader.validate()
        data = self.data_loader.load()
        normalized_data = self.data_loader.normalize()
        config_hash = self.audit_trail.hash_file(self.config_loader.config_path)
        data_hash = self.audit_trail.hash_file(self.data_loader.data_path)
        # Registrar por periodo
        periodos = data['Periodo'].unique()
        for periodo in periodos:
            datos_periodo = data[data['Periodo'] == periodo]
            fecha_recoleccion = datos_periodo['Fecha_recoleccion'].iloc[0]
            fecha_carga = datos_periodo['Fecha_carga'].iloc[0]
            run_id = self.audit_trail.register(config_hash, data_hash, carrera_id, config['version_modelo'], periodo, fecha_recoleccion, fecha_carga)
            print(f"Ejecución SSD completa. run_id: {run_id}, periodo: {periodo}")
