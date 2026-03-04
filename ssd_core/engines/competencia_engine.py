# competencia_engine.py
# Motor de cálculo de competencias (no compensatorio)
import pandas as pd

class CompetenciaEngine:
	def __init__(self, competencia_data, ra_data):
		# Homologar nombres de columnas
		self.competencia_data = competencia_data.rename(columns={
			'ID_Competencia': 'ID_COMP',
			'ID_RA': 'ID_RA',
			'Peso_RA_en_Competencia': 'PESO_RA_EN_COMPETENCIA'
		})
		self.ra_data = ra_data.rename(columns={
			'competencia_id': 'ID_COMP',
			'ra_id': 'ID_RA'
		})

	def calculate(self, student_id):
		# Calcula el logro de cada competencia como suma ponderada de los RA alcanzados
		competencias = {}
		for comp in self.competencia_data['ID_COMP'].unique():
			comp_rows = self.competencia_data[self.competencia_data['ID_COMP'] == comp]
			total = 0.0
			for _, row in comp_rows.iterrows():
				ra = row['ID_RA']
				peso = float(row['PESO_RA_EN_COMPETENCIA'])
				# Busca el valor alcanzado para ese RA por el estudiante
				ra_row = self.ra_data[(self.ra_data['ID_COMP'] == comp) & (self.ra_data['ID_RA'] == ra)]
				if not ra_row.empty:
					valor = float(ra_row.iloc[0]['valor_minimo'])
				else:
					valor = 0.0
				total += peso * valor
			competencias[comp] = total
		return competencias