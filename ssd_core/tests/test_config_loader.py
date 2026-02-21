# test_config_loader.py
import unittest
from base.config_loader import ConfigLoader
import os

class TestConfigLoader(unittest.TestCase):
    def test_load_and_validate(self):
        config_path = os.path.join('config', 'model_config.yaml')
        loader = ConfigLoader(config_path)
        config = loader.load()
        self.assertTrue(loader.validate())
        self.assertIn('version_modelo', config)

if __name__ == '__main__':
    unittest.main()
