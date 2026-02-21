# audit_trail.py
# Clase para registrar auditoría
import uuid
import json
import time
import hashlib

class AuditTrail:
    def __init__(self, output_dir):
        self.output_dir = output_dir

    def register(self, config_hash, data_hash, carrera_id, version_modelo):
        run_id = str(uuid.uuid4())
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        audit_data = {
            'run_id': run_id,
            'timestamp': timestamp,
            'version_modelo': version_modelo,
            'hash_configuracion': config_hash,
            'hash_datos_entrada': data_hash,
            'carrera_id': carrera_id
        }
        file_path = os.path.join(self.output_dir, f'audit_{run_id}.json')
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(audit_data, f, indent=2)
        return run_id

    @staticmethod
    def hash_file(file_path):
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
