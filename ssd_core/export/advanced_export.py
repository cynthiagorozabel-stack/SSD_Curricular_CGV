# advanced_export.py
# -----------------------------------------------------------------------------
# Exportación "avanzada": recibe una lista de diccionarios (filas de la tabla de
# hechos de indicadores) y la escribe como un único CSV en el directorio de
# exportación, sobrescribiendo el archivo si ya existe.
# -----------------------------------------------------------------------------
import os

import pandas as pd


def export_advanced(results, export_dir, filename):
    """Escribe `results` (lista de dicts o DataFrame) como CSV. Devuelve la ruta."""
    os.makedirs(export_dir, exist_ok=True)
    path = os.path.join(export_dir, filename)
    df = results if isinstance(results, pd.DataFrame) else pd.DataFrame(results)
    df.to_csv(path, index=False)
    return path
