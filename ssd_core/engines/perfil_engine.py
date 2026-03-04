# perfil_engine.py
# Motor de cálculo de perfil de egreso
import pandas as pd

class PerfilEngine:
	def __init__(self, perfil_data, competencia_results):
		# Homologar nombres de columnas
		self.perfil_data = perfil_data.rename(columns={
			'perfil_id': 'ID_PERFIL',
			'competencia_id': 'ID_COMP'
		})
		self.competencia_results = competencia_results

	def calculate(self):
		# Ejemplo: perfil por suma ponderada de competencias
		perfil = {}
		for perfil_id in self.perfil_data['ID_PERFIL'].unique():
			perfil_comp = self.perfil_data[self.perfil_data['ID_PERFIL'] == perfil_id]
			valor = sum(
				self.competencia_results.get(row['ID_COMP'], 0) * row['peso']
				for _, row in perfil_comp.iterrows()
			)
			perfil[perfil_id] = valor
		return perfil