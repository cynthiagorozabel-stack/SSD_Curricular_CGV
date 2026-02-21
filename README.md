# SSD Curricular

Sistema de Soporte a la Decisión curricular para aseguramiento de calidad académica.

## Estructura
- Modular, auditable y extensible.
- Configuración y datos en archivos csv/yaml.

## Ejecución
1. Subir archivos de datos y configuración.
2. Ejecutar `python main.py --carrera_id=...`.
3. Outputs y auditoría en carpetas export/audit.

## Pruebas
- Ejecutar pruebas unitarias en `ssd_core/tests` con `python -m unittest discover tests`.

## Documentación
- Ver `Diseño_Conceptual.md` para el modelo y metodología.

## Repositorio
- Recomendado como repositorio privado en GitHub.
