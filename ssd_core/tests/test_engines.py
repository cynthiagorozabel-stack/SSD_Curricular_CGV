# test_engines.py
import os
import sys
import unittest
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from ssd_core.engines.ra_engine import RAEngine
from ssd_core.engines.competencia_engine import CompetenciaEngine
from ssd_core.engines.perfil_engine import PerfilEngine


class TestRAEngine(unittest.TestCase):
    def setUp(self):
        self.asignaturas = pd.DataFrame({
            'COD_ASIGNATURA': ['CALV1', 'ALGL1', 'COMLV'],
            'RA': ['RA1', 'RA1', 'RA5'],
        })
        self.engine = RAEngine(self.asignaturas)

    def test_promedio_de_asignaturas_del_mismo_ra(self):
        matric = pd.DataFrame({
            'ID_EST': ['E1', 'E1', 'E1'],
            'COD_ASIGNATURA': ['CALV1', 'ALGL1', 'COMLV'],
            'Nota': [80, 60, 90],
            'ID_Cohorte': ['O2010-1'] * 3,
            'Nivel': ['PRIMER'] * 3,
        })
        result = self.engine.calculate(matric, fecha_corte='2026-09-30')
        ra1 = result[(result['ID_EST'] == 'E1') & (result['RA'] == 'RA1')].iloc[0]
        self.assertAlmostEqual(ra1['Logro_RA'], 70.0)
        ra5 = result[(result['ID_EST'] == 'E1') & (result['RA'] == 'RA5')].iloc[0]
        self.assertAlmostEqual(ra5['Logro_RA'], 90.0)
        self.assertEqual(ra1['ID_Cohorte'], 'O2010-1')

    def test_ignora_notas_no_numericas(self):
        matric = pd.DataFrame({
            'ID_EST': ['E1', 'E1'],
            'COD_ASIGNATURA': ['CALV1', 'ALGL1'],
            'Nota': [80, 'NA'],
        })
        result = self.engine.calculate(matric)
        self.assertAlmostEqual(result.iloc[0]['Logro_RA'], 80.0)


class TestCompetenciaEngine(unittest.TestCase):
    def setUp(self):
        self.mapa = pd.DataFrame({
            'ra_id': ['RA1', 'RA2', 'RA3'],
            'ID_COMP': ['C1', 'C1', 'C2'],
            'valor_minimo': [0.7, 0.7, 0.7],
        })
        self.engine = CompetenciaEngine(self.mapa)

    def test_no_compensatorio_usa_el_minimo_y_registra_limitante(self):
        ra_logro = pd.DataFrame({
            'ID_EST': ['E1', 'E1', 'E1'],
            'RA': ['RA1', 'RA2', 'RA3'],
            'Logro_RA': [40.0, 90.0, 85.0],
            'ID_Cohorte': ['O2010-1'] * 3,
        })
        result = self.engine.calculate(ra_logro, fecha_corte='2026-09-30')
        c1 = result[(result['ID_EST'] == 'E1') & (result['ID_COMP'] == 'C1')].iloc[0]
        c2 = result[(result['ID_EST'] == 'E1') & (result['ID_COMP'] == 'C2')].iloc[0]
        self.assertAlmostEqual(c1['Logro_Competencia'], 40.0)
        self.assertEqual(c1['ra_limitante'], 'RA1')
        self.assertAlmostEqual(c2['Logro_Competencia'], 85.0)
        self.assertNotEqual(c1['Logro_Competencia'], c2['Logro_Competencia'])

    def test_ra_alto_no_compensa_ra_bajo(self):
        ra_logro = pd.DataFrame({
            'ID_EST': ['E1', 'E1'],
            'ID_RA': ['RA1', 'RA2'],
            'Logro_RA': [100.0, 10.0],
        })
        result = self.engine.calculate(ra_logro)
        c1 = result[result['ID_COMP'] == 'C1'].iloc[0]
        self.assertAlmostEqual(c1['Logro_Competencia'], 10.0)
        self.assertEqual(c1['ra_limitante'], 'RA2')

    def test_ra_ausente_no_cuenta_como_cero(self):
        ra_logro = pd.DataFrame({
            'ID_EST': ['E1'],
            'ID_RA': ['RA2'],
            'Logro_RA': [88.0],
        })
        result = self.engine.calculate(ra_logro)
        c1 = result[result['ID_COMP'] == 'C1'].iloc[0]
        self.assertAlmostEqual(c1['Logro_Competencia'], 88.0)
        self.assertEqual(c1['ra_limitante'], 'RA2')
        self.assertFalse((result['ID_COMP'] == 'C2').any())


class TestPerfilEngine(unittest.TestCase):
    def setUp(self):
        self.mapa = pd.DataFrame({
            'perfil_id': ['P1', 'P1'],
            'ID_COMP': ['C1', 'C2'],
            'peso': [0.70, 0.30],
        })
        self.engine = PerfilEngine(self.mapa)

    def test_suma_ponderada_con_pesos_del_csv(self):
        comp = pd.DataFrame({
            'ID_EST': ['E1', 'E1'],
            'ID_COMP': ['C1', 'C2'],
            'Logro_Competencia': [40.0, 90.0],
        })
        result = self.engine.calculate(comp)
        p1 = result[(result['ID_EST'] == 'E1') & (result['ID_PERFIL'] == 'P1')].iloc[0]
        self.assertAlmostEqual(p1['Logro_Perfil'], 0.70 * 40.0 + 0.30 * 90.0)

    def test_renormaliza_si_falta_una_competencia(self):
        comp = pd.DataFrame({
            'ID_EST': ['E1'],
            'ID_COMP': ['C1'],
            'Logro_Competencia': [40.0],
        })
        result = self.engine.calculate(comp)
        p1 = result.iloc[0]
        self.assertAlmostEqual(p1['Logro_Perfil'], 40.0)


class TestCadenaCurricular(unittest.TestCase):
    def test_ra_competencia_perfil_con_oraculo(self):
        asignaturas = pd.DataFrame({
            'COD_ASIGNATURA': ['A1', 'A2', 'A3'],
            'RA': ['RA1', 'RA2', 'RA3'],
        })
        matric = pd.DataFrame({
            'ID_EST': ['E1', 'E1', 'E1'],
            'COD_ASIGNATURA': ['A1', 'A2', 'A3'],
            'Nota': [45, 90, 80],
        })
        ra_map = pd.DataFrame({
            'ra_id': ['RA1', 'RA2', 'RA3'],
            'ID_COMP': ['C1', 'C1', 'C2'],
        })
        perfil_map = pd.DataFrame({
            'perfil_id': ['P1', 'P1'],
            'competencia_id': ['C1', 'C2'],
            'peso': [0.7, 0.3],
        })
        ra = RAEngine(asignaturas).calculate(matric)
        comp = CompetenciaEngine(ra_map).calculate(ra)
        perfil = PerfilEngine(perfil_map).calculate(comp)
        c1 = comp[comp['ID_COMP'] == 'C1'].iloc[0]
        self.assertEqual(c1['ra_limitante'], 'RA1')
        self.assertAlmostEqual(c1['Logro_Competencia'], 45.0)
        esperado = 0.7 * 45.0 + 0.3 * 80.0
        self.assertAlmostEqual(perfil.iloc[0]['Logro_Perfil'], esperado)


if __name__ == '__main__':
    unittest.main()
