"""
Genera un archivo de alimentación para el cálculo del ISPG, consolidando toda la información relevante por cohorte.
Si algún dato no existe, se deja vacío.
"""
import pandas as pd
import numpy as np
import os

def preparar_alimento_ispg(export_dir='export'):
    # Cargar archivos fuente
    beg_path = os.path.join(export_dir, 'beg_cohorte.csv')
    ri_path = os.path.join(export_dir, 'riesgos_internos_individual.csv')
    re_path = os.path.join(export_dir, 'riesgos_externos_individual.csv')

    # Cargar BEG
    if os.path.exists(beg_path):
        beg = pd.read_csv(beg_path)
    else:
        beg = pd.DataFrame()
    # Cargar riesgos internos
    if os.path.exists(ri_path):
        ri = pd.read_csv(ri_path)
    else:
        ri = pd.DataFrame()
    # Cargar riesgos externos
    if os.path.exists(re_path):
        re = pd.read_csv(re_path)
    else:
        re = pd.DataFrame()

    # Normalizar claves
    for df in [beg, ri, re]:
        if not df.empty:
            if 'ID_Cohorte' in df.columns:
                df['ID_Cohorte'] = df['ID_Cohorte'].astype(str).str.strip()
            if 'Periodo' in df.columns:
                df['Periodo'] = df['Periodo'].astype(str).str.strip()

    # Agrupar riesgos internos por cohorte
    if not ri.empty and 'ID_Cohorte' in ri.columns:
        if 'desempeño' in ri.columns:
            # Normalizar desempeño a [0,1] si es necesario
            max_desempeno = ri['desempeño'].max()
            if max_desempeno > 1:
                ri['desempeño_norm'] = ri['desempeño'] / 100.0
            else:
                ri['desempeño_norm'] = ri['desempeño']
            ri['desempeño_norm'] = ri['desempeño_norm'].clip(lower=0, upper=1)
            ri['riesgo_interno'] = 1 - ri['desempeño_norm']
        else:
            ri['riesgo_interno'] = np.nan
        ri_cohorte = ri.groupby('ID_Cohorte')['riesgo_interno'].mean().reset_index()
    else:
        ri_cohorte = pd.DataFrame(columns=['ID_Cohorte','riesgo_interno'])

    # Agrupar riesgos externos por cohorte
    if not re.empty and 'ID_Cohorte' in re.columns:
        if 'empleabilidad' in re.columns and 'satisfacción' in re.columns:
            re['riesgo_externo'] = 1 - (re['empleabilidad'] + re['satisfacción'])/2
        else:
            re['riesgo_externo'] = np.nan
        re_cohorte = re.groupby('ID_Cohorte')['riesgo_externo'].mean().reset_index()
    else:
        re_cohorte = pd.DataFrame(columns=['ID_Cohorte','riesgo_externo'])

    # Merge por cohorte y periodo
    if not beg.empty:
        df = beg.copy()
        df = df.merge(ri_cohorte, on='ID_Cohorte', how='left')
        df = df.merge(re_cohorte, on='ID_Cohorte', how='left')
    else:
        # Si no hay BEG, crear estructura vacía
        df = pd.DataFrame(columns=['ID_Cohorte','Periodo','BEG','riesgo_interno','riesgo_externo'])

    # Ordenar columnas y rellenar vacíos
    columnas = ['ID_Cohorte','Periodo','BEG','riesgo_interno','riesgo_externo','nivel_esperado','Perfil_Promedio_Cohorte','Fecha_corte','Fecha_generacion_indicador','Fuente_datos','Nivel_maximo']
    for col in columnas:
        if col not in df.columns:
            df[col] = np.nan
    df = df[columnas]
    # Exportar archivo de alimento
    out_path = os.path.join(export_dir, 'alimento_ispg.csv')
    df.to_csv(out_path, index=False)
    print(f"Archivo de alimento ISPG generado: {out_path}")

if __name__ == '__main__':
    preparar_alimento_ispg()
