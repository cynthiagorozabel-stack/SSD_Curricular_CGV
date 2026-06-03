# Manual de Uso Profesional: SSD Curricular

## 1. ¿Qué es el SSD Curricular?
El **Sistema de Soporte a la Decisión Curricular (SSD Curricular)** es una plataforma modular, auditable y extensible diseñada para el aseguramiento de la calidad académica en instituciones de educación superior. Permite evaluar, auditar y mejorar el diseño curricular de múltiples carreras, integrando datos internos y externos, riesgos, indicadores y trazabilidad, con el objetivo de sustentar procesos de acreditación y mejora continua.

## 2. ¿Para qué sirve?
- **Aseguramiento de calidad curricular**: Evalúa el cumplimiento de resultados de aprendizaje (RA), competencias y perfil de egreso.
- **Trazabilidad y auditoría**: Cada ejecución es auditable, con registro de configuración, datos, versión y resultados.
- **Integración de riesgos**: Analiza riesgos internos (desempeño, repitencia, deserción) y externos (empleabilidad, satisfacción, contexto socioeconómico).
- **Exportación y visualización**: Resultados listos para análisis en Power BI y sistemas externos (ACTUA).
- **Simulación y validación**: Permite pruebas robustas mediante generación de datos simulados y validaciones estadísticas.

## 3. Metodología y Modelo
### Jerarquía Curricular
- **RA (Resultados de Aprendizaje) → Competencia → Perfil de Egreso**
- **Modelo no compensatorio**: Cada competencia depende del RA más débil (mínimo cumplimiento relativo), sin compensación entre RA.
- **Motores de riesgo**: Cálculo de riesgos internos y externos, BEG (Brecha Estructural de Egreso) e ISPG (Indicador Sintético de Progreso Global).
- **Validaciones**: Integridad, mínimos, pesos, alertas, y validaciones estadísticas (Alpha de Cronbach, sensibilidad, Monte Carlo).

## 4. Estructura del Sistema
```
SSD_CGV_V2/
│   requirements.txt
│   README.md
│   ...
└───ssd_core/
    │   main.py
    ├───base/
    ├───engines/
    ├───validation/
    ├───export/
    ├───simulation/
    └───config/
```
- **main.py**: Orquestador principal.
- **base/**: Carga y validación de configuración y datos, auditoría.
- **engines/**: Motores de cálculo de RA, competencias, perfil, riesgos, BEG, ISPG.
- **validation/**: Validaciones estadísticas y de integridad.
- **export/**: Exportación de resultados.
- **simulation/**: Generación de datos simulados.
- **config/**: Archivos de configuración y mapeos.

## 5. Flujo de Uso
1. **Preparar archivos de datos y configuración** en la carpeta `ssd_core/config` (ver ejemplos y plantillas).
2. **Activar el entorno virtual**:
   - En PowerShell: `& venv\Scripts\Activate.ps1`
3. **Ejecutar el sistema**:
   - `python ssd_core/main.py --carrera_id=...`
4. **Revisar outputs** en las carpetas `export/` y `audit/`.
5. **Visualizar y analizar resultados** en Power BI o sistemas externos.

## 6. Desglose de la Metodología
- **Configuración 100% en archivos**: Todos los parámetros, pesos, mínimos y mapeos están en archivos csv/yaml.
- **Pipeline modular**: Cada motor (RA, competencia, perfil, riesgos) es independiente y auditable.
- **Auditoría robusta**: Cada ejecución genera un archivo JSON con run_id, timestamp, versión, hash de configuración y datos.
- **Validaciones estadísticas**: Alpha de Cronbach, análisis de sensibilidad y simulación Monte Carlo para robustez.
- **Simulación**: `run_example.py` permite generar datasets sintéticos para pruebas y validación.

## 7. Ejemplo de Configuración de Riesgos (model_config.yaml)
```yaml
riesgos:
  internos:
    - archivo: riesgos_internos.csv
      columnas: [desempeño, repitencia, deserción]
  externos:
    - archivo: riesgos_externos.csv
      columnas: [empleabilidad, satisfacción]
```

## 8. Sustento para Tesis
El SSD Curricular implementa una arquitectura profesional, auditable y reproducible, alineada con estándares internacionales de aseguramiento de calidad. Su diseño modular permite la extensión a nuevas carreras, reglas y motores, facilitando la investigación y mejora continua. La trazabilidad y validación estadística garantizan la robustez de los resultados, aportando evidencia sólida para procesos de acreditación y publicaciones académicas.

## 9. Referencias y Documentación
- **Diseño y metodología**: Ver `Diseño_Conceptual.md`.
- **Guía de entorno y ejecución**: Ver `GUÍA_PYTHONPATH.md`.
- **Pruebas unitarias**: Ejecutar `python -m unittest discover ssd_core/tests`.
- **Requisitos**: Ver `requirements.txt`.

---

**Este manual respalda el uso profesional y académico del SSD Curricular, sirviendo como base documental para tesis, acreditación y mejora institucional.**
