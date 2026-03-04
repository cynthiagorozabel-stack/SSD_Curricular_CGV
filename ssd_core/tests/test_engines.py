# test_engines.py
import unittest
import pandas as pd
from ssd_core.engines.ra_engine import RAEngine
from ssd_core.engines.competencia_engine import CompetenciaEngine
from ssd_core.engines.perfil_engine import PerfilEngine

class TestEngines(unittest.TestCase):
    def test_ra_engine(self):
        data = pd.DataFrame({
            'ID_EST': ['E1', 'E2'],
            'ID_RA': ['RA1', 'RA2'],
            'ID_COMP': ['C1', 'C2'],
            'valor_minimo': [0.7, 0.8]
        })
        engine = RAEngine(data)
        result = engine.calculate('E1')
        self.assertFalse(result.empty)

    def test_competencia_engine(self):
        comp_data = pd.DataFrame({
            'ID_COMP': ['C1', 'C1', 'C2'],
            'ID_RA': ['RA1', 'RA2', 'RA3'],
            'PESO_RA_EN_COMPETENCIA': [0.5, 0.5, 1.0]
        })
        ra_data = pd.DataFrame({
            'ID_RA': ['RA1', 'RA2', 'RA3'],
            'ID_COMP': ['C1', 'C1', 'C2'],
            'valor_minimo': [0.7, 0.8, 0.9]
        })
        engine = CompetenciaEngine(comp_data, ra_data)
        result = engine.calculate('E1')
        self.assertIn('C1', result)
        self.assertIn('C2', result)

    def test_perfil_engine(self):
        perfil_data = pd.DataFrame({
            'ID_PERFIL': ['P1'],
            'ID_COMP': ['C1'],
            'peso': [0.5]
        })
        competencia_results = {'C1': 0.7}
        engine = PerfilEngine(perfil_data, competencia_results)
        result = engine.calculate()
        self.assertIn('P1', result)
        competencia_results = {'C1': 0.7}
        engine = PerfilEngine(perfil_data, competencia_results)
        result = engine.calculate()
        self.assertIn('P1', result)

if __name__ == '__main__':
    unittest.main()
