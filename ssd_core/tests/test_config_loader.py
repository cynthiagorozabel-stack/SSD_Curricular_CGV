
# test_config_loader.py
import unittest
import os
import sys
# Asegura que la raíz del proyecto esté en PYTHONPATH para imports absolutos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from ssd_core.base.config_loader import ConfigLoader

class TestConfigLoader(unittest.TestCase):
    def test_load_and_validate(self):
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'model_config.yaml')
        config_path = os.path.abspath(config_path)
        loader = ConfigLoader(config_path)
        config = loader.load()
        self.assertTrue(loader.validate())
        self.assertIn('version_modelo', config)

if __name__ == '__main__':
    unittest.main()
