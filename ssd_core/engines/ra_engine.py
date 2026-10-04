# ra_engine.py
# Logro de Resultados de Aprendizaje a partir de notas de asignatura.
import pandas as pd


def _rename_existing(df, aliases):
    rename = {}
    for src, dst in aliases.items():
        if src in df.columns and dst not in df.columns:
            rename[src] = dst
    return df.rename(columns=rename)


class RAEngine:
    """Asignatura → RA: promedio de notas numéricas por estudiante y RA."""

    def __init__(self, asignaturas):
        asig = asignaturas.copy()
        asig = _rename_existing(asig, {
            'Materia': 'COD_ASIGNATURA',
            'RA_ID': 'RA',
            'ID_RA': 'RA',
        })
        if 'COD_ASIGNATURA' not in asig.columns or 'RA' not in asig.columns:
            raise ValueError('asignaturas debe incluir COD_ASIGNATURA y RA')
        self.asignaturas = asig.dropna(subset=['COD_ASIGNATURA', 'RA'])

    def calculate(self, matriculacion, fecha_corte=None):
        matric = matriculacion.copy()
        matric = _rename_existing(matric, {
            'Estudiante_ID': 'ID_EST',
            'estudiante_id': 'ID_EST',
            'Materia': 'COD_ASIGNATURA',
        })
        if 'ID_EST' not in matric.columns or 'COD_ASIGNATURA' not in matric.columns:
            raise ValueError('matriculacion debe incluir ID_EST y COD_ASIGNATURA')
        if 'Nota' not in matric.columns:
            raise ValueError('matriculacion debe incluir Nota')

        mapa = self.asignaturas.drop_duplicates('COD_ASIGNATURA').set_index('COD_ASIGNATURA')['RA']
        matric['RA'] = matric['COD_ASIGNATURA'].map(mapa)
        matric = matric[matric['RA'].notna()]
        matric['Nota'] = pd.to_numeric(matric['Nota'], errors='coerce')
        matric = matric.dropna(subset=['Nota'])

        ra_logro = (
            matric.groupby(['ID_EST', 'RA'], as_index=False)
            .agg(Logro_RA=('Nota', 'mean'))
        )
        ra_logro['ID_RA'] = ra_logro['RA']
        fecha = fecha_corte or pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        ra_logro['Fecha_corte'] = fecha

        meta_cols = [c for c in ['ID_Cohorte', 'Nivel'] if c in matric.columns]
        if meta_cols:
            meta = matric.drop_duplicates('ID_EST')[['ID_EST'] + meta_cols]
            ra_logro = ra_logro.merge(meta, on='ID_EST', how='left')
        return ra_logro
