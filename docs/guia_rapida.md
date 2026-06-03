# Guía Rápida para usar SSD_CGV_V2

## ¿Qué hace este proyecto?
SSD_CGV_V2 es un sistema de aseguramiento de calidad curricular que calcula indicadores académicos y de riesgo basados en resultados de aprendizaje, competencias y perfil de egreso. Genera resultados auditable y exportables para análisis.

## ¿Dónde está la documentación importante?
- `docs/README.md`: índice central de la documentación.
- `docs/introduccion.md`: qué es el proyecto y su propósito.
- `docs/uso.md`: pasos básicos de ejecución.
- `docs/MANUAL_USO_SSD_CURRICULAR.md`: manual completo para uso profesional.
- `docs/Diseño_Conceptual.md`: diseño y modelo arquitectónico.
- `docs/GUÍA_PYTHONPATH.md`: cómo ejecutar scripts y tests con PYTHONPATH.

## Requisitos mínimos
1. Tener Python instalado.
2. Activar el entorno virtual:
   - PowerShell: `& venv\Scripts\Activate.ps1`
3. Instalar dependencias:
   - `pip install -r requirements.txt`

## Ejecución rápida
1. Desde la raíz del proyecto, abre PowerShell.
2. Activa el entorno virtual:
   - `& venv\Scripts\Activate.ps1`
3. Ejecuta el sistema principal:
   - `python ssd_core/main.py --carrera_id=101`
4. Si necesitas generar la matriculación histórica, usa el ejecutable del programa:
   - `python ssd_core/main.py --generar_matriculacion_historica`
   - Este archivo histórico no debe subirse a GitHub.
5. Revisa los resultados en:
   - `export/`
   - `audit/`

## Qué archivos ver primero
- `docs/introduccion.md`: para comprender el propósito general.
- `docs/uso.md`: para saber cómo ejecutar el sistema.
- `docs/estructura.md`: para entender la organización del proyecto.
- `docs/Diseño_Conceptual.md`: para conocer el diseño técnico completo.

## Consejos para un usuario nuevo
- Empieza por leer `docs/introduccion.md` y `docs/uso.md`.
- Usa `docs/GUÍA_PYTHONPATH.md` si tienes problemas con imports o tests.
- Para entender el método detrás de los cálculos, revisa `docs/logica_exportacion.md` y `docs/analisis_fiabilidad.md`.
- Si necesitas una visión profesional y un manual de referencia, abre `docs/MANUAL_USO_SSD_CURRICULAR.md`.

## Resultado final
Al finalizar, tendrás:
- Resultados exportados en `export/`.
- Auditoría en `audit/`.
- Documentación organizada en `docs/` para cualquier nuevo usuario.
