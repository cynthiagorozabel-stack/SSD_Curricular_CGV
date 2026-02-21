# montecarlo.py
# Validación estadística: Simulación Monte Carlo
import numpy as np

class MonteCarloValidator:
	def __init__(self, data):
		self.data = data

	def simulate(self, n=1000):
		# Simulación simple Monte Carlo
		results = []
		for _ in range(n):
			sample = self.data.sample(frac=1, replace=True)
			results.append(sample.mean().mean())
		return {'montecarlo_mean': np.mean(results), 'montecarlo_std': np.std(results)}