# competencia_engine.py
# Competencia no compensatoria: mínimo de RA mapeados y RA limitante.
import pandas as pd


def _rename_existing(df, aliases):
    rename = {}
    for src, dst in aliases.items():
        if src in df.columns and dst not in df.columns:
            rename[src] = dst
    return df.rename(columns=rename)


class CompetenciaEngine:
    """RA → competencia: min(Logro_RA) sobre el mapeo curricular; registra ra_limitante.

    Un RA alto no compensa uno bajo. Solo cuentan los RA que el estudiante
    tiene evaluados; un RA ausente no se trata como cero.
    """

    def __init__(self, ra_competencia):
        mapa = ra_competencia.copy()
        mapa = _rename_existing(mapa, {
            'ra_id': 'ID_RA',
            'RA_ID': 'ID_RA',
            'RA': 'ID_RA',
            'competencia_id': 'ID_COMP',
            'ID_Competencia': 'ID_COMP',
        })
        if 'ID_RA' not in mapa.columns or 'ID_COMP' not in mapa.columns:
            raise ValueError('ra_competencia debe incluir ID_RA (o ra_id) e ID_COMP')
        cols = ['ID_RA', 'ID_COMP']
        if 'valor_minimo' in mapa.columns:
            cols.append('valor_minimo')
        self.mapa = mapa[cols].drop_duplicates(['ID_RA', 'ID_COMP'])

    def calculate(self, ra_logro, fecha_corte=None):
        ra = ra_logro.copy()
        ra = _rename_existing(ra, {
            'RA': 'ID_RA',
            'ra_id': 'ID_RA',
            'RA_ID': 'ID_RA',
        })
        if 'ID_RA' not in ra.columns and 'RA' in ra_logro.columns:
            ra['ID_RA'] = ra_logro['RA']
        if 'Logro_RA' not in ra.columns:
            raise ValueError('ra_logro debe incluir Logro_RA')
        if 'ID_EST' not in ra.columns:
            raise ValueError('ra_logro debe incluir ID_EST')

        merged = ra.merge(self.mapa, on='ID_RA', how='inner')
        if merged.empty:
            return pd.DataFrame(columns=[
                'ID_EST', 'ID_COMP', 'Logro_Competencia', 'ra_limitante', 'Fecha_corte'
            ])

        merged = merged.sort_values(['ID_EST', 'ID_COMP', 'Logro_RA', 'ID_RA']).reset_index(drop=True)
        limitantes = merged.loc[
            merged.groupby(['ID_EST', 'ID_COMP'])['Logro_RA'].idxmin()
        ]
        fecha = fecha_corte or pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        result = limitantes[['ID_EST', 'ID_COMP', 'Logro_RA', 'ID_RA']].rename(columns={
            'Logro_RA': 'Logro_Competencia',
            'ID_RA': 'ra_limitante',
        })
        result['Fecha_corte'] = fecha
        meta_cols = [c for c in ['ID_Cohorte', 'Nivel'] if c in ra.columns]
        if meta_cols:
            meta = ra.drop_duplicates('ID_EST')[['ID_EST'] + meta_cols]
            result = result.merge(meta, on='ID_EST', how='left')
        return result.reset_index(drop=True)
