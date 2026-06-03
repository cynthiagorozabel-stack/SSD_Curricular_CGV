# test_audit_trail.py
import unittest
from ssd_core.base.audit_trail import AuditTrail
import os

class TestAuditTrail(unittest.TestCase):
    def test_hash_file_and_register(self):
        audit_dir = 'audit'
        config_path = os.path.join('config', 'model_config.yaml')
        data_path = os.path.join('config', 'ra_competencia.csv')
        audit = AuditTrail(audit_dir)
        config_hash = audit.hash_file(config_path)
        data_hash = audit.hash_file(data_path)
        run_id = audit.register(config_hash, data_hash, 101, '1.0')
        self.assertIsNotNone(run_id)

if __name__ == '__main__':
    unittest.main()
