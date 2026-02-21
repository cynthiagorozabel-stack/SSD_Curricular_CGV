# competencia_engine.py
# Motor de cálculo de competencias (no compensatorio)
import pandas as pd

class CompetenciaEngine:
	def __init__(self, competencia_data, ra_data):
		self.competencia_data = competencia_data
		self.ra_data = ra_data

	def calculate(self, student_id):
		# Ejemplo: calcular competencia por RA mínimo
		competencias = {}
		for comp in self.competencia_data['competencia_id'].unique():
			ra_values = self.ra_data[self.ra_data['competencia_id'] == comp]['valor_minimo']
			competencias[comp] = ra_values.min() if not ra_values.empty else None
		return competencias