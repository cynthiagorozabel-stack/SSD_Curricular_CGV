
"""
beg_engine.py
Cálculo de la Brecha Estructural del Egresado (BEG) para el SSD.
"""
import pandas as pd
import numpy as np

class BEGEngine:
    """
    Calcula la Brecha Estructural del Egresado (BEG) para cada perfil de egreso.
    BEG = max(0, nivel_esperado - valor_perfil)
    NOTA: Ahora la escala es 0-100 (nivel_esperado y valor_perfil en 0-100).
    """
    def __init__(self, perfil_promedio_path, config_path):
        self.perfil_promedio_path = perfil_promedio_path
        self.config_path = config_path
        self.df_perfil = pd.read_csv(perfil_promedio_path)
        self.nivel_esperado = self._load_nivel_esperado()

    def _load_nivel_esperado(self):
        """
        Cargar nivel esperado desde config (puede ser un valor único, por cohorte o por perfil).
        Se recomienda agregar en model_config.yaml:
        nivel_esperado: 0.8
        # o bien
        nivel_esperado_cohorte:
          O2010-1: 0.8
          O2011-1: 0.82
        """
        import yaml
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        if 'nivel_esperado_cohorte' in config:
            return config['nivel_esperado_cohorte']
        elif 'nivel_esperado' in config:
            return config['nivel_esperado']
        else:
            return 0.8

    def calcular_beg(self):
        """
        Calcula BEG por cohorte: BEG = max(0, nivel_esperado - Perfil_Promedio_Cohorte)
        Si nivel_esperado es dict, se usa por cohorte; si es float/int, se usa para todos.
        Escala: 0-100.
        """
        df = self.df_perfil.copy()
        # Determinar nivel esperado (puede ser único o por cohorte)
        if isinstance(self.nivel_esperado, dict):
            df['nivel_esperado'] = df['ID_Cohorte'].map(self.nivel_esperado)
        else:
            df['nivel_esperado'] = self.nivel_esperado
        # Calcular BEG en escala 0-100
        df['BEG'] = (df['nivel_esperado'] - df['Perfil_Promedio_Cohorte']).clip(lower=0)
        # Trazabilidad y robustez
        cols = ['ID_Cohorte', 'Periodo', 'Perfil_Promedio_Cohorte', 'nivel_esperado', 'BEG']
        for col in ['Fecha_corte', 'Fecha_generacion_indicador', 'Fuente_datos', 'Nivel_maximo']:
            if col in df.columns:
                cols.append(col)
        return df[cols]

    def exportar_beg(self, export_path):
        beg_df = self.calcular_beg()
        beg_df.to_csv(export_path, index=False)
        return export_path