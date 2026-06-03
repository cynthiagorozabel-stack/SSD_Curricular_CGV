# calcular_ispg.py
# -----------------------------------------------------------------------------
# Cálculo independiente del ISPG (Indicador Sintético de Progreso Global) y del
# resumen BEG/ISPG por cohorte, a partir de los archivos ya generados por el
# pipeline principal (ssd_core/main.py).
#
# ¿Por qué un archivo aparte?
#   El bloque BEG/ISPG dentro de main.py falla ('>' not supported between str and
#   int) cuando una cohorte aún no tiene graduados (su BEG queda vacío). Para NO
#   modificar la lógica de indicadores de main.py, este script la reproduce de
#   forma idéntica pero calcula el ISPG SOLO para las cohortes con BEG definido
#   (las que ya tienen graduados en NOVENO).
#
# No se cambia nada del modelo:
#   - Definición de BEG = 100 - promedio de Logro_Perfil en NOVENO (idéntica a main.py).
#   - Fórmula ISPG = 0.50*BEG - 0.30*Riesgo_interno - 0.20*Riesgo_externo (idéntica).
#   - Pesos (0.50 / 0.30 / 0.20) y umbrales de clasificación (Verde/Amarillo/Rojo) idénticos.
#
# Uso (desde la raíz del proyecto, después de ejecutar main.py):
#   python calcular_ispg.py
# -----------------------------------------------------------------------------
import os
import glob
import json
from datetime import datetime

import numpy as np
import pandas as pd


def _ultimo_alpha_cronbach(export_dir='export'):
    """Devuelve el alpha de Cronbach más reciente exportado por main.py, o ''."""
    archivos = glob.glob(os.path.join(export_dir, 'alpha_cronbach_*.json'))
    if not archivos:
        return ''
    ultimo = max(archivos, key=os.path.getmtime)
    try:
        with open(ultimo, 'r', encoding='utf-8') as f:
            return json.load(f).get('alpha_cronbach', '')
    except Exception:
        return ''


def main():
    perfil_logro_path = 'export/perfil_logro_individual.csv'
    matric_path = 'ssd_core/config/matriculacion_historica_test.csv'
    riesgos_int_path = 'export/riesgos_internos_individual.csv'
    riesgos_ext_path = os.path.join('ssd_core', 'config', 'riesgos_externos.csv')
    salida_path = 'export/BEG_ISPG_M.csv'

    if not os.path.exists(perfil_logro_path):
        print(f'No se encontró {perfil_logro_path}. Ejecute primero ssd_core/main.py.')
        return

    # --- Datos base (idéntico a main.py) ---
    matric = pd.read_csv(matric_path)
    perfil_logro = pd.read_csv(perfil_logro_path)
    if 'ID_Cohorte' not in perfil_logro.columns:
        raise ValueError('perfil_logro_individual.csv debe contener la columna ID_Cohorte.')
    perfil_logro['Logro_Perfil'] = pd.to_numeric(perfil_logro['Logro_Perfil'], errors='coerce')
    perfil_logro = perfil_logro.dropna(subset=['Logro_Perfil'])

    fecha_analisis = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    fuente_datos = perfil_logro_path
    fecha_carga = perfil_logro['Fecha_corte'].iloc[0] if 'Fecha_corte' in perfil_logro.columns else ''

    # --- BEG / PRE_BEG por cohorte (idéntico a main.py) ---
    niveles_orden = ['PRIMER', 'SEGUNDO', 'TERCERO', 'CUARTO', 'QUINTO', 'SEXTO', 'SEPTIMO', 'OCTAVO', 'NOVENO']
    resumenes = []
    for cohorte, grupo in perfil_logro.groupby('ID_Cohorte'):
        N = len(grupo)
        ests_cohorte = grupo['ID_EST'].unique()
        niveles_est = matric[matric['ID_EST'].isin(ests_cohorte)]['Nivel'].dropna().str.upper().unique().tolist()
        nivel_analisis = ''
        for n in reversed(niveles_orden):
            if n in niveles_est:
                nivel_analisis = n
                break
        # BEG: estudiantes con logros en NOVENO nivel
        est_noveno = matric[(matric['ID_EST'].isin(ests_cohorte)) & (matric['Nivel'].str.upper() == 'NOVENO')]['ID_EST'].unique()
        grupo_noveno = grupo[grupo['ID_EST'].isin(est_noveno)]
        promedio_noveno = round(grupo_noveno['Logro_Perfil'].mean(), 2) if not grupo_noveno.empty else 0
        beg = round(100 - promedio_noveno, 2) if promedio_noveno else ''
        # PRE_BEG: estudiantes con logros en OCTAVO nivel
        est_octavo = matric[(matric['ID_EST'].isin(ests_cohorte)) & (matric['Nivel'].str.upper() == 'OCTAVO')]['ID_EST'].unique()
        grupo_octavo = grupo[grupo['ID_EST'].isin(est_octavo)]
        promedio_octavo = round(grupo_octavo['Logro_Perfil'].mean(), 2) if not grupo_octavo.empty else 0
        pre_beg = round(100 - promedio_octavo, 2) if promedio_octavo else ''
        resumenes.append({
            'ID_Cohorte': cohorte,
            'N': N,
            'Nivel_Analisis': nivel_analisis,
            'Promedio_Logro_Perfil_Noveno': promedio_noveno,
            'BEG': beg,
            'PRE_BEG': pre_beg,
            'Fuente_datos': fuente_datos,
            'Fecha_carga': fecha_carga,
            'Fecha_analisis': fecha_analisis,
        })
    if not resumenes:
        print('No hay datos numéricos válidos en Logro_Perfil para calcular BEG/ISPG.')
        return
    resumen_df = pd.DataFrame(resumenes)

    # --- Riesgos y ISPG (idéntico a main.py) ---
    riesgos_int = pd.read_csv(riesgos_int_path)
    riesgos_ext = pd.read_csv(riesgos_ext_path)
    est_to_cohorte = perfil_logro.set_index('ID_EST')['ID_Cohorte'].to_dict()
    riesgos_int['ID_Cohorte'] = riesgos_int['ID_EST'].map(est_to_cohorte) if 'ID_EST' in riesgos_int.columns else None
    riesgos_ext['ID_Cohorte'] = riesgos_ext['estudiante_id'].map(est_to_cohorte) if 'estudiante_id' in riesgos_ext.columns else None
    if 'desempeño' in riesgos_int.columns:
        riesgos_int['riesgo_interno'] = riesgos_int[['desempeño', 'repitencia', 'deserción']].mean(axis=1)
    if 'empleabilidad' in riesgos_ext.columns:
        riesgos_ext['riesgo_externo'] = riesgos_ext[['empleabilidad', 'satisfacción']].mean(axis=1)
    # Riesgo externo global: mediana de las cohortes de los últimos 5 años
    cohortes_ordenadas = sorted(resumen_df['ID_Cohorte'].unique(), reverse=True)
    cohortes_ultimos_5 = cohortes_ordenadas[:5]
    valores_ultimos_5 = riesgos_ext[riesgos_ext['ID_Cohorte'].isin(cohortes_ultimos_5)]['riesgo_externo'] if 'riesgo_externo' in riesgos_ext.columns else []
    riesgo_ext_global = float(np.median(valores_ultimos_5)) if len(valores_ultimos_5) > 0 else 0
    riesgo_int_cohorte = riesgos_int.groupby('ID_Cohorte')['riesgo_interno'].mean() if 'riesgo_interno' in riesgos_int.columns else pd.Series(dtype=float)

    alpha = _ultimo_alpha_cronbach()

    resumenes_final = []
    for _, row in resumen_df.iterrows():
        # ÚNICA diferencia con main.py: se omiten las cohortes sin BEG (sin graduados),
        # para las que el ISPG no está definido. No se altera ninguna fórmula ni peso.
        if row['BEG'] == '' or pd.isna(row['BEG']):
            continue
        cohorte = row['ID_Cohorte']
        beg = row['BEG'] / 100 if row['BEG'] > 1 else row['BEG']
        riesgo_int = riesgo_int_cohorte.get(cohorte, 0)
        riesgo_ext = riesgo_ext_global
        ispg = 0.50 * beg - 0.30 * riesgo_int - 0.20 * riesgo_ext
        ispg_norm = max(0, min(1, ispg))
        if ispg_norm >= 0.75:
            clasificacion = 'Verde'
        elif ispg_norm >= 0.60:
            clasificacion = 'Amarillo'
        else:
            clasificacion = 'Rojo'
        resumenes_final.append({
            'ID_Cohorte': cohorte,
            'N': row['N'],
            'Nivel_Analisis': row['Nivel_Analisis'],
            'Promedio_Logro_Perfil_Noveno': row['Promedio_Logro_Perfil_Noveno'],
            'BEG': row['BEG'],
            'PRE_BEG': row['PRE_BEG'],
            'Riesgo_interno': round(riesgo_int, 3),
            'Riesgo_externo': round(riesgo_ext, 3),
            'ISPG': round(ispg, 3),
            'ISPG_norm': round(ispg_norm, 3),
            'Clasificacion': clasificacion,
            'Fuente_datos': row['Fuente_datos'],
            'Fecha_carga': row['Fecha_carga'],
            'Fecha_analisis': row['Fecha_analisis'],
            'Alpha_Cronbach': alpha if alpha is not None else '',
            'MonteCarlo_mean': '',
            'MonteCarlo_std': '',
        })

    if resumenes_final:
        resumen_df_final = pd.DataFrame(resumenes_final)
        resumen_df_final.to_csv(salida_path, index=False)
        print(f'Exportado: {salida_path} ({len(resumen_df_final)} cohortes graduadas con ISPG)')
    else:
        print('No hay cohortes graduadas (con BEG definido) para calcular el ISPG.')


if __name__ == '__main__':
    main()
