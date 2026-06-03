"""
Calcula el ISPG por cohorte usando el archivo alimento_ispg.csv generado previamente.
Genera un archivo export/ispg_individual.csv con los resultados.
"""
import pandas as pd
import numpy as np
import os

def calcular_ispg_alimento(export_dir='export'):
    in_path = os.path.join(export_dir, 'alimento_ispg.csv')
    out_path = os.path.join(export_dir, 'ispg_individual.csv')
    if not os.path.exists(in_path):
        print(f"No existe archivo de alimento: {in_path}")
        return
    df = pd.read_csv(in_path)
    if df.empty:
        print("El archivo de alimento está vacío.")
        return
    # Normalizar BEG, riesgo_interno y riesgo_externo a [0,1] y sin negativos
    for col in ['BEG','riesgo_interno','riesgo_externo']:
        if col in df.columns:
            df[col] = df[col].clip(lower=0)
            max_val = df[col].max()
            if max_val > 0:
                df[col+'_norm'] = df[col] / max_val
            else:
                df[col+'_norm'] = 0
        else:
            df[col+'_norm'] = np.nan
    # Calcular ISPG con los valores normalizados
    df['ISPG'] = 0.50 * df['BEG_norm'] - 0.30 * df['riesgo_interno_norm'] - 0.20 * df['riesgo_externo_norm']
    df['ISPG'] = df['ISPG'].clip(lower=0)
    df['ISPG_norm'] = df['ISPG'].clip(0, 1)
    df['clasificacion'] = pd.cut(df['ISPG_norm'], bins=[-np.inf,0.60,0.75,np.inf], labels=['Rojo','Amarillo','Verde'])
    # Reordenar columnas
    cols = ['ID_Cohorte','Periodo','BEG','BEG_norm','riesgo_interno','riesgo_interno_norm','riesgo_externo','riesgo_externo_norm','ISPG','ISPG_norm','clasificacion','nivel_esperado','Perfil_Promedio_Cohorte','Fecha_corte','Fecha_generacion_indicador','Fuente_datos','Nivel_maximo']
    for col in cols:
        if col not in df.columns:
            df[col] = np.nan
    df = df[cols]
    df.to_csv(out_path, index=False)
    print(f"ISPG calculado y exportado en: {out_path}")

if __name__ == '__main__':
    calcular_ispg_alimento()
