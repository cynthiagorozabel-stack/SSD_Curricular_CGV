# sensibilidad.py
# Validación estadística: Análisis de sensibilidad
import numpy as np

class SensibilidadValidator:
	def __init__(self, data):
		self.data = data

	def analyze(self):
		# Usar solo columnas numéricas para el análisis
		items = self.data.select_dtypes(include=['number'])
		if items.shape[1] == 0:
			print("[SensibilidadValidator] No hay columnas numéricas para analizar.")
			return {'sensibilidad': None}
		return {'sensibilidad': np.std(items.values)}