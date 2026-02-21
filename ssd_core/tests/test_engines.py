# test_engines.py
import unittest
import pandas as pd
from engines.ra_engine import RAEngine
from engines.competencia_engine import CompetenciaEngine
from engines.perfil_engine import PerfilEngine

class TestEngines(unittest.TestCase):
    def test_ra_engine(self):
        data = pd.DataFrame({'estudiante_id': ['E1', 'E2'], 'competencia_id': ['C1', 'C2'], 'valor_minimo': [0.7, 0.8]})
        engine = RAEngine(data)
        result = engine.calculate('E1')
        self.assertFalse(result.empty)

    def test_competencia_engine(self):
        comp_data = pd.DataFrame({'competencia_id': ['C1', 'C2']})
        ra_data = pd.DataFrame({'competencia_id': ['C1', 'C2'], 'valor_minimo': [0.7, 0.8]})
        engine = CompetenciaEngine(comp_data, ra_data)
        result = engine.calculate(None)
        self.assertIn('C1', result)

    def test_perfil_engine(self):
        perfil_data = pd.DataFrame({'perfil_id': ['P1'], 'competencia_id': ['C1'], 'peso': [0.5]})
        competencia_results = {'C1': 0.7}
        engine = PerfilEngine(perfil_data, competencia_results)
        result = engine.calculate()
        self.assertIn('P1', result)

if __name__ == '__main__':
    unittest.main()
