# 6. Uso y Ejecución

1. Activar el entorno virtual: `venv`.
2. Ejecutar el pipeline principal:
   ```
   $env:PYTHONPATH = '.'; python ssd_core/main.py --carrera_id=101
   ```
3. Si necesitas generar la matriculación histórica, usa el ejecutable del programa:
   ```
   python ssd_core/main.py --generar_matriculacion_historica
   ```
   - Este archivo se crea desde el propio sistema.
   - No es necesario subir el archivo generado a GitHub.
4. Los resultados se generan en la carpeta `export/`.
5. Consultar los archivos de análisis y trazabilidad para validación y auditoría.