
# 3. Lógica de Cálculo y Exportación

Todos los cálculos y exportaciones se centralizan en `ssd_core/main.py`.

## Archivos de salida principales (actuales)

- `export/ra_logro_matrix.csv`: Matriz de logros individuales por estudiante y RA (Resultado de Aprendizaje). Incluye identificadores, notas, cohortes y trazabilidad (run_id, timestamp, versión del modelo).
- `export/ra_logro_individual.csv`: Logros individuales por estudiante y RA.
- `export/competencia_logro_individual.csv`: Logros individuales por estudiante y competencia.
- `export/perfil_logro_individual.csv`: Logros individuales por estudiante y perfil de egreso.
- `export/riesgos_internos_individual.csv`: Riesgos internos calculados por estudiante (desempeño, repitencia, deserción, etc.).
- `export/riesgos_externos_individual.csv`: Riesgos externos por estudiante (empleabilidad, satisfacción, etc.).
- `export/resultados_avanzados.csv`: Exportación avanzada con todos los indicadores calculados, lista para análisis externo.
- `export/alpha_cronbach_<run_id>.json`: Resultados de validación estadística (fiabilidad, alfa de Cronbach) para trazabilidad.

Todos los archivos incluyen campos de trazabilidad: run_id, timestamp_export, versión_modelo, fuente de datos y parámetros clave.

## Usos de los archivos exportados

### Con Power BI
- Los archivos CSV pueden ser importados directamente a Power BI para visualización, dashboards y análisis interactivo.
- La estructura tabular y la trazabilidad permiten filtrar por cohorte, periodo, indicador, etc.
- Los archivos avanzados (`resultados_avanzados.csv`) permiten construir reportes integrados de logros, riesgos y perfiles.

### Sin Power BI
- Los archivos pueden ser abiertos en Excel, LibreOffice o cualquier software de análisis de datos.
- Permiten auditoría manual, revisión de cohortes, análisis estadístico y generación de reportes personalizados.
- Los archivos JSON de validación pueden ser usados para documentación y control de calidad.

## Notas
- El sistema ya no exporta archivos de BEG/ISPG ni realiza análisis de brecha estructural global.
- Toda la lógica de exportación es auditable y reproducible, con identificadores únicos por ejecución.