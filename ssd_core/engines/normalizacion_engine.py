# normalizacion_engine.py
# Motor de normalización de datos
import pandas as pd

import os

class NormalizacionEngine:
	def __init__(self, data, diccionario_path=None):
		self.data = data
		if diccionario_path is None:
			# Ruta por defecto relativa al archivo actual
			diccionario_path = os.path.join(os.path.dirname(__file__), '../config/diccionario_variables.csv')
		self.diccionario_path = os.path.abspath(diccionario_path)

	def columnas_requeridas(self):
		import pandas as pd
		dicc = pd.read_csv(self.diccionario_path)
		return list(dicc['ID_Variable'].dropna().unique())

	def columnas_faltantes(self):
		requeridas = set(self.columnas_requeridas())
		presentes = set(self.data.columns)
		return list(requeridas - presentes)

	def normalize(self, verbose=True):
		# Verifica columnas faltantes y reporta
		faltantes = self.columnas_faltantes()
		if verbose and faltantes:
			print(f"[NormalizacionEngine] Columnas faltantes: {faltantes}")
		# Normalización simple
		return self.data.fillna(0)