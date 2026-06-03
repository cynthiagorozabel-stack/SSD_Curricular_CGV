import pandas as pd
from datetime import datetime, timedelta

class IndicadoresActualesEngine:
    def exportar_perfil_promedio_cohorte(self, perfil_promedio_path, export_path):
        """
        Exporta el Perfil_Promedio_Cohorte para las cohortes de los últimos 3 años, con trazabilidad.
        """
        df = pd.read_csv(perfil_promedio_path)
        # Filtrar por los últimos 3 años completos usando la columna 'Periodo'
        df = self._filtrar_ultimos_tres_anios_por_periodo(df, 'Periodo')
        # Agrupar por ID_Cohorte y calcular el promedio de PERFIL_Promedio
        resumen = df.groupby('ID_Cohorte').agg({
            'PERFIL_Promedio': 'mean',
            'Periodo': 'last',
            'Fecha_corte': 'last',
        }).reset_index()
        resumen = resumen.rename(columns={'PERFIL_Promedio': 'Perfil_Promedio_Cohorte'})
        # Trazabilidad
        from datetime import datetime
        resumen['Fecha_generacion_indicador'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        resumen['Fuente_datos'] = perfil_promedio_path
        resumen.to_csv(export_path, index=False)
        print(f'Exportado: {export_path}')
        def calcular_perfil_general(self, perfil_promedio_path):
            """
            Calcula el perfil general promedio de las últimas cohortes de los últimos 3 años.
            """
            df = pd.read_csv(perfil_promedio_path)
            # Filtrar por los últimos 3 años completos usando la columna 'Periodo'
            df = self._filtrar_ultimos_tres_anios_por_periodo(df, 'Periodo')
            # Agrupar por ID_EST y obtener el promedio de PERFIL_Promedio
            resumen = df.groupby('ID_EST').agg({
                'PERFIL_Promedio': 'mean',
                'Periodo': 'last',
                'ID_Cohorte': 'last',
                'Fecha_corte': 'last',
                'Nivel': 'last'
            }).reset_index()
            resumen = resumen.rename(columns={'PERFIL_Promedio': 'Perfil_General'})
            return resumen
    """
    Motor para calcular y exportar:
    1. Indicador Actual Externo (síntesis de riesgos externos últimos 3 años)
    2. Indicador Actual Interno (síntesis de riesgos internos últimos 3 años)
    """
    def __init__(self, riesgos_externos_path, riesgos_internos_path):
        self.riesgos_externos_path = riesgos_externos_path
        self.riesgos_internos_path = riesgos_internos_path
        self.df_ext = pd.read_csv(riesgos_externos_path)
        self.df_int = pd.read_csv(riesgos_internos_path)

    def _filtrar_ultimos_tres_anios_por_periodo(self, df, periodo_col='Periodo'):
        """
        Filtra el DataFrame para dejar solo los periodos correspondientes a los últimos 3 años completos.
        El formato de periodo debe ser 'YYYY-X', donde X es el número de periodo en el año.
        """
        # Extraer año de cada periodo
        df = df.copy()
        df['__anio'] = df[periodo_col].astype(str).str.extract(r'(\d{4})').astype(float)
        # Determinar los 3 años más recientes con datos
        anios = sorted(df['__anio'].dropna().unique())
        if len(anios) == 0:
            return df.iloc[0:0]  # DataFrame vacío
        ultimos_tres = anios[-3:]
        df_filtrado = df[df['__anio'].isin(ultimos_tres)].drop(columns='__anio')
        return df_filtrado

    def calcular_indicador_externo(self):
        # Filtrar últimos 3 años completos por periodo
        df = self._filtrar_ultimos_tres_anios_por_periodo(self.df_ext, 'Periodo')
        # Identificar columnas externas numéricas (ej: empleabilidad, satisfacción)
        ext_cols = [col for col in df.columns if col not in ['ID_EST','Periodo','Fecha_corte','ID_Cohorte','estudiante_id'] and df[col].dtype != 'O']
        df = df.copy()
        # Normalizar cada columna a 0-100 (mayor es mejor)
        for col in ext_cols:
            minv = df[col].min()
            maxv = df[col].max()
            if maxv > minv:
                df[col + '_norm'] = 100 * (df[col] - minv) / (maxv - minv)
            else:
                df[col + '_norm'] = 100  # Si todos son iguales, es óptimo
        norm_cols = [col + '_norm' for col in ext_cols]
        df['Indicador_Actual_Externo'] = df[norm_cols].mean(axis=1)
        resumen = df.groupby('ID_EST')['Indicador_Actual_Externo'].mean().reset_index()
        return resumen

    def calcular_indicador_interno(self):
        # Filtrar últimos 3 años completos por periodo
        df = self._filtrar_ultimos_tres_anios_por_periodo(self.df_int, 'Periodo')
        # Normalización de variables
        # Desempeño: ya está en 1-100
        # Repitencia: normalizar inversamente (más repite, peor)
        # Deserción: 0 (no desertó, bueno), 1 (desertó, malo)
        df = df.copy()
        # Normalizar repitencia
        rep_min = df['repitencia'].min()
        rep_max = df['repitencia'].max()
        if rep_max > rep_min:
            df['repitencia_norm'] = 100 * (1 - (df['repitencia'] - rep_min) / (rep_max - rep_min))
        else:
            df['repitencia_norm'] = 100  # Si todos son iguales, no penaliza
        # Normalizar deserción
        df['desercion_norm'] = 100 * (1 - df['deserción'].astype(float))
        # Desempeño ya está en escala 1-100
        df['desempeño_norm'] = df['desempeño'].astype(float)
        # Indicador final: promedio de los normalizados
        df['Indicador_Actual_Interno'] = df[['desempeño_norm','repitencia_norm','desercion_norm']].mean(axis=1)
        resumen = df.groupby('ID_EST')['Indicador_Actual_Interno'].mean().reset_index()
        return resumen

    def exportar_indicadores(self, export_path, perfil_promedio_path):
        ext = self.calcular_indicador_externo()
        inte = self.calcular_indicador_interno()
        perfil = self.calcular_perfil_general(perfil_promedio_path)
        # Unir todo por ID_EST
        resultado = ext.merge(inte, on='ID_EST', how='outer').merge(perfil, on='ID_EST', how='outer')
        # Agregar trazabilidad: periodos y fecha de extracción
        from datetime import datetime
        resultado['Fecha_extraccion'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Exportar
        resultado.to_csv(export_path, index=False)
        print(f'Exportado: {export_path}')
