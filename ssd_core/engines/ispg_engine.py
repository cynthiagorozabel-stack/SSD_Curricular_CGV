
"""
ispg_engine.py
Cálculo del Indicador de Satisfacción del Programa General (ISPG) para el SSD.
"""
import pandas as pd
import numpy as np

class ISPGEngine:
    """
    Calcula el ISPG integrando BEG, riesgo interno y riesgo externo.
    Fórmula de síntesis (escala 0-100):
        ISPG = 0.50 × BEG - 0.30 × riesgo_interno - 0.20 × riesgo_externo
    Donde:
        - BEG: Brecha de Egreso Global (0=óptimo, 100=máxima brecha)
        - riesgo_interno: Riesgo de gestión interna (0=bajo, 100=alto)
        - riesgo_externo: Riesgo de contexto externo (0=bajo, 100=alto)
    Normalización:
        ISPG_norm = clip(ISPG/100, 0, 1)  # Fuerza rango [0,1]
    Clasificación:
        Verde   ≥ 0.75  : ISPG es alto, riesgos bajos
        Amarillo 0.60-0.75 : ISPG es medio, necesita monitoreo
        Rojo    < 0.60  : ISPG es bajo, requiere acción
    """
    def __init__(self, beg_path, riesgo_interno_path, riesgo_externo_path):
        self.df_beg = pd.read_csv(beg_path)
        self.df_ri = pd.read_csv(riesgo_interno_path)
        self.df_re = pd.read_csv(riesgo_externo_path)

    def calcular_ispg(self):
        # Adaptado para calcular ISPG por cohorte
        df_beg = self.df_beg.copy()
        # Riesgo interno: promedio por cohorte
        if 'ID_Cohorte' in self.df_ri.columns:
            if 'desempeño' in self.df_ri.columns:
                self.df_ri['riesgo_interno'] = 1 - self.df_ri['desempeño']
            else:
                self.df_ri['riesgo_interno'] = self.df_ri.mean(axis=1)
            df_ri_cohorte = self.df_ri.groupby('ID_Cohorte')['riesgo_interno'].mean().reset_index()
        else:
            raise ValueError('riesgos_internos_individual.csv debe tener columna ID_Cohorte')

        # Riesgo externo: promedio por cohorte
        if 'ID_Cohorte' in self.df_re.columns:
            if 'empleabilidad' in self.df_re.columns and 'satisfacción' in self.df_re.columns:
                self.df_re['riesgo_externo'] = 1 - (self.df_re['empleabilidad'] + self.df_re['satisfacción'])/2
            else:
                self.df_re['riesgo_externo'] = self.df_re.mean(axis=1)
            df_re_cohorte = self.df_re.groupby('ID_Cohorte')['riesgo_externo'].mean().reset_index()
        else:
            raise ValueError('riesgos_externos_individual.csv debe tener columna ID_Cohorte')

        # Unir por ID_Cohorte y Periodo
        merge_cols = ['ID_Cohorte', 'Periodo'] if 'Periodo' in df_beg.columns else ['ID_Cohorte']
        df = df_beg.copy()
        df = df.merge(df_ri_cohorte, on='ID_Cohorte', how='left')
        df = df.merge(df_re_cohorte, on='ID_Cohorte', how='left')
        # Calcular ISPG (escala 0-100)
        df['ISPG'] = 0.50 * df['BEG'] - 0.30 * df['riesgo_interno'] - 0.20 * df['riesgo_externo']
        # Normalizar ISPG al rango [0,1] para clasificación
        df['ISPG_norm'] = (df['ISPG'] / 100).clip(0, 1)
        # Clasificación según ISPG normalizado
        df['clasificacion'] = pd.cut(df['ISPG_norm'], bins=[-np.inf,0.60,0.75,np.inf], labels=['Rojo','Amarillo','Verde'])
        # Columnas de salida
        cols = ['ID_Cohorte','Periodo','BEG','riesgo_interno','riesgo_externo','ISPG','ISPG_norm','clasificacion']
        for col in ['Fecha_corte', 'Fecha_generacion_indicador', 'Fuente_datos', 'Nivel_maximo']:
            if col in df.columns:
                cols.append(col)
        return df[cols]

    def exportar_ispg(self, export_path):
        ispg_df = self.calcular_ispg()
        ispg_df.to_csv(export_path, index=False)
        return export_path