# config_loader.py
# Clase para cargar y validar configuración
import yaml
import os

class ConfigLoader:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = None

    def load(self):
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        return self.config

    def validate(self):
        # Validación básica
        if not self.config:
            raise ValueError('Configuración no cargada')
        if 'version_modelo' not in self.config:
            raise ValueError('Falta version_modelo en configuración')
        return True
