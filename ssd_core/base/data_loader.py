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
        return self.data

    def normalize(self):
        # Normalización simple (placeholder)
        if self.data is not None:
            return self.data.fillna(0)
        return None
