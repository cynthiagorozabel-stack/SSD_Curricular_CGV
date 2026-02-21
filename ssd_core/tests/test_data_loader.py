# test_data_loader.py
import unittest
from base.data_loader import DataLoader
import os

class TestDataLoader(unittest.TestCase):
    def test_load_and_normalize(self):
        data_path = os.path.join('config', 'ra_competencia.csv')
        loader = DataLoader(data_path)
        data = loader.load()
        normalized = loader.normalize()
        self.assertIsNotNone(data)
        self.assertIsNotNone(normalized)

if __name__ == '__main__':
    unittest.main()
