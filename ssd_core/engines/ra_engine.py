# ra_engine.py
# Motor de cálculo de Resultados de Aprendizaje (RA)
import pandas as pd

class RAEngine:
	def __init__(self, ra_data):
		self.ra_data = ra_data

	def calculate(self, student_id):
		# Ejemplo: filtrar RA por estudiante
		return self.ra_data[self.ra_data['estudiante_id'] == student_id]