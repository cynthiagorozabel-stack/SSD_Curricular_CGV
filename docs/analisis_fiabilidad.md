# 4. Análisis de Fiabilidad y Simulación: Alpha de Cronbach y Monte Carlo

## Alpha de Cronbach
- Mide la fiabilidad interna de los indicadores (RA, desempeño, etc.) en la matriz `export/ra_logro_matrix.csv`.
- Se calcula solo si hay al menos dos columnas numéricas.
- Un valor alto indica coherencia interna; un valor bajo sugiere revisar los indicadores.
- Riesgos: valores muy altos pueden indicar redundancia; valores bajos, falta de coherencia.

## Monte Carlo
- Simula escenarios aleatorios sobre la matriz de logros para estimar la robustez de los resultados.
- Se reportan la media y desviación estándar de los resultados simulados.
- Riesgos: depende de la calidad de los datos y supuestos de variabilidad.

## Importancia
- Ambos resultados se integran en `export/BEG_ISPG_analisis.csv` para trazabilidad y validación de calidad.
- Permiten validar la consistencia y robustez antes de tomar decisiones.