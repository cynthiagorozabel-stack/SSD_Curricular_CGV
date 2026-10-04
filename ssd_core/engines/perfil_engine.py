# perfil_engine.py
# Perfil de egreso: suma ponderada de competencias según competencia_perfil.csv.
import pandas as pd


def _rename_existing(df, aliases):
    rename = {}
    for src, dst in aliases.items():
        if src in df.columns and dst not in df.columns:
            rename[src] = dst
    return df.rename(columns=rename)


class PerfilEngine:
    """Competencia → perfil: sum(peso * Logro_Competencia) / sum(pesos disponibles).

    Los pesos salen solo de competencia_perfil.csv. Si falta una competencia
    (estudiante que aún no la cursa), se renormaliza sobre las que sí tiene.
    """

    def __init__(self, competencia_perfil):
        mapa = competencia_perfil.copy()
        mapa = _rename_existing(mapa, {
            'perfil_id': 'ID_PERFIL',
            'competencia_id': 'ID_COMP',
            'ID_Competencia': 'ID_COMP',
        })
        if 'peso' not in mapa.columns:
            raise ValueError('competencia_perfil debe incluir peso')
        if 'ID_PERFIL' not in mapa.columns or 'ID_COMP' not in mapa.columns:
            raise ValueError('competencia_perfil debe incluir perfil_id e ID_COMP')
        mapa['peso'] = pd.to_numeric(mapa['peso'], errors='coerce')
        self.mapa = mapa.dropna(subset=['peso'])[['ID_PERFIL', 'ID_COMP', 'peso']]

    def calculate(self, competencia_logro, student_meta=None, fecha_corte=None):
        comp = competencia_logro.copy()
        comp = _rename_existing(comp, {
            'competencia_id': 'ID_COMP',
            'ID_Competencia': 'ID_COMP',
        })
        if 'ID_EST' not in comp.columns or 'ID_COMP' not in comp.columns:
            raise ValueError('competencia_logro debe incluir ID_EST e ID_COMP')
        if 'Logro_Competencia' not in comp.columns:
            raise ValueError('competencia_logro debe incluir Logro_Competencia')

        merged = comp.merge(self.mapa, on='ID_COMP', how='inner')
        if merged.empty:
            return pd.DataFrame(columns=[
                'ID_EST', 'ID_PERFIL', 'Logro_Perfil', 'Fecha_corte'
            ])

        merged['ponderado'] = merged['peso'] * merged['Logro_Competencia']
        grouped = merged.groupby(['ID_EST', 'ID_PERFIL'], as_index=False).agg(
            ponderado=('ponderado', 'sum'),
            peso_total=('peso', 'sum'),
        )
        grouped = grouped[grouped['peso_total'] > 0]
        grouped['Logro_Perfil'] = grouped['ponderado'] / grouped['peso_total']
        fecha = fecha_corte or pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        result = grouped[['ID_EST', 'ID_PERFIL', 'Logro_Perfil']].copy()
        result['Fecha_corte'] = fecha

        meta_src = student_meta if student_meta is not None else comp
        meta_cols = [c for c in ['ID_Cohorte', 'Nivel', 'Periodo'] if c in meta_src.columns]
        if meta_cols:
            meta = meta_src.drop_duplicates('ID_EST')[['ID_EST'] + meta_cols]
            result = result.merge(meta, on='ID_EST', how='left')
        return result.reset_index(drop=True)
