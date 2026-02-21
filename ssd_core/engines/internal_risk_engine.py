# internal_risk_engine.py
# Motor de cálculo de riesgos internos
import pandas as pd

class InternalRiskEngine:
	def __init__(self, risk_data):
		self.risk_data = risk_data

	def calculate(self, student_id):
		# Ejemplo: filtrar riesgos internos por estudiante
		return self.risk_data[self.risk_data['estudiante_id'] == student_id]