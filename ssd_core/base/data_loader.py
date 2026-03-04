# data_loader.py
# Clase para cargar y normalizar datos
import pandas as pd
import os

class DataLoader:
    def __init__(self, data_path):
        self.data_path = data_path
        self.data = None

    def load(self):
        self.data = pd.read_csv(self.data_path)
        # Determinar si es archivo de dimensión (dim o mapeo) o histórico
        filename = os.path.basename(self.data_path).lower()
        if filename.startswith('dim_') or filename in ['ra_competencia.csv', 'competencia_perfil.csv', 'dim_competencia.csv']:
            required_cols = ['Fecha_recoleccion', 'Fecha_carga']
        else:
            required_cols = ['Periodo', 'Fecha_recoleccion', 'Fecha_carga']
        for col in required_cols:
            if col not in self.data.columns:
                raise ValueError(f"Falta columna de trazabilidad: {col}")
        return self.data

    def normalize(self):
        # Normalización simple (placeholder)
        if self.data is not None:
            return self.data.fillna(0)
        return None
