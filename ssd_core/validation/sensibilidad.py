# sensibilidad.py
# Validación estadística: Análisis de sensibilidad
import numpy as np

class SensibilidadValidator:
	def __init__(self, data):
		self.data = data

	def analyze(self):
		# Placeholder: análisis de sensibilidad
		return {'sensibilidad': np.std(self.data.values)}