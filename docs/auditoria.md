# 5. Auditoría y Trazabilidad

- Cada ejecución genera un `run_id` único y archivos de auditoría en la carpeta `audit/`.
- Todos los archivos exportados incluyen columnas de trazabilidad: run_id, timestamp, versión de modelo, fuente de datos.
- Esto permite reconstruir y auditar cualquier resultado a posteriori.