# 3. Lógica de Cálculo y Exportación

- Todos los cálculos y exportaciones se centralizan en `ssd_core/main.py`.
- Los indicadores (logros, riesgos, BEG, ISPG) se calculan a partir de datos reales de matrícula y desempeño.
- Las exportaciones incluyen trazabilidad (run_id, fechas, fuentes).
- Los archivos principales de salida son:
  - `export/ra_logro_matrix.csv`
  - `export/riesgos_externos_individual.csv`
  - `export/BEG_ISPG_analisis.csv`
  - `export/BEG_logro.csv`, `export/ISPG_logro.csv`