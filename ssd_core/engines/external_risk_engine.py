# external_risk_engine.py
# Motor de cálculo de riesgos externos
import pandas as pd

class ExternalRiskEngine:
	def __init__(self, risk_data):
		# Homologar nombre de columna
		self.risk_data = risk_data.rename(columns={'estudiante_id': 'ID_EST'})

	def calculate(self, student_id):
		# Filtrar riesgos externos por estudiante
		return self.risk_data[self.risk_data['ID_EST'] == student_id]