# powerbi_export.py
# -----------------------------------------------------------------------------
# Motor de exportación mínimo: escribe un DataFrame (o estructura tabular) a un
# archivo CSV dentro del directorio de exportación. No realiza ninguna conexión
# ni transformación hacia Power BI; el análisis visual se hace en Power BI a
# partir de los CSV generados aquí.
# -----------------------------------------------------------------------------
import os

import pandas as pd


class ExportEngine:
    def __init__(self, export_dir):
        self.export_dir = export_dir
        os.makedirs(self.export_dir, exist_ok=True)

    def export(self, data, filename):
        """Escribe `data` como CSV en export_dir/filename y devuelve la ruta."""
        path = os.path.join(self.export_dir, filename)
        df = data if isinstance(data, pd.DataFrame) else pd.DataFrame(data)
        df.to_csv(path, index=False)
        return path
