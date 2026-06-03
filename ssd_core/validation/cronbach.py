# cronbach.py
# Validación estadística: Alpha de Cronbach
import numpy as np
import pandas as pd

class CronbachValidator:
	def __init__(self, data):
		self.data = data

	def calculate_alpha(self):
		# Usar solo columnas numéricas
		items = self.data.select_dtypes(include=['number'])
		n_items = items.shape[1]
		if n_items < 2:
			print("[CronbachValidator] Se requieren al menos dos columnas numéricas para calcular alfa de Cronbach.")
			print(f"Columnas numéricas detectadas: {list(items.columns)}")
			return None
		variances = items.var(axis=0, ddof=1)
		total_var = items.sum(axis=1).var(ddof=1)
		if total_var == 0:
			return 0.0
		alpha = (n_items / (n_items - 1)) * (1 - variances.sum() / total_var)
		return alpha