# ra_engine.py
# Motor de cálculo de Resultados de Aprendizaje (RA)
import pandas as pd

class RAEngine:
	def __init__(self, ra_data):
		# Homologar nombre de columna
		self.ra_data = ra_data.rename(columns={'estudiante_id': 'ID_EST'})

	def calculate(self, student_id):
		# Filtrar RA por estudiante
		return self.ra_data[self.ra_data['ID_EST'] == student_id]