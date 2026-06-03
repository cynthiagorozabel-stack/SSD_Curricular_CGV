# montecarlo.py
# Validación estadística: Simulación Monte Carlo
import numpy as np

class MonteCarloValidator:
	def __init__(self, data):
		self.data = data

	def simulate(self, n=1000):
		# Simulación simple Monte Carlo solo con columnas numéricas
		numeric_data = self.data.select_dtypes(include=['number'])
		if numeric_data.shape[1] == 0:
			print("[MonteCarloValidator] No se encontraron columnas numéricas para la simulación Monte Carlo.")
			return {'montecarlo_mean': None, 'montecarlo_std': None}
		results = []
		for _ in range(n):
			sample = numeric_data.sample(frac=1, replace=True)
			results.append(sample.mean().mean())
		return {'montecarlo_mean': np.mean(results), 'montecarlo_std': np.std(results)}