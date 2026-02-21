# normalizacion_engine.py
# Motor de normalización de datos
import pandas as pd

class NormalizacionEngine:
	def __init__(self, data):
		self.data = data

	def normalize(self):
		# Ejemplo: normalización simple
		return self.data.fillna(0)