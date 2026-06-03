# 10. Bitácora y Control de Versiones

## Objetivo
Documentar de manera exhaustiva y sistemática todos los cambios, decisiones, incidencias y versiones del Sistema de Seguimiento de Desempeño (SSD Curricular), asegurando trazabilidad, reproducibilidad y auditoría científica.

## Estructura de la Bitácora
- **Fecha:** Día y hora exacta del cambio o evento.
- **run_id:** Identificador único de la ejecución o versión.
- **Responsable:** Persona o equipo que realizó la acción.
- **Descripción:** Detalle claro y conciso del cambio, corrección, mejora o incidencia.
- **Archivos afectados:** Lista de archivos modificados, creados o eliminados.
- **Motivo:** Justificación técnica, científica o administrativa del cambio.
- **Impacto:** Efectos esperados en resultados, indicadores, trazabilidad o usuarios.
- **Fuente de datos:** Origen de los datos utilizados o modificados.
- **Versión del modelo:** Hash o número de versión del modelo de cálculo utilizado.
- **Validación/Auditoría:** Resultado de pruebas, validaciones o auditorías asociadas al cambio.

## Reglas de Registro
- Todo cambio debe ser registrado antes de su despliegue en producción.
- Las entradas deben ser cronológicas y no editables retroactivamente (solo se permiten adendas).
- Se recomienda el uso de herramientas de control de versiones (Git) y la exportación periódica de la bitácora en formato seguro (PDF, CSV).
- Cada ejecución relevante del sistema debe generar automáticamente una entrada con su `run_id` y parámetros clave.

## Ejemplo de Entrada de Bitácora
| Fecha                | run_id      | Responsable | Descripción                                 | Archivos afectados                | Motivo                | Impacto                  | Fuente de datos | Versión modelo | Validación/Auditoría |
|----------------------|------------|-------------|----------------------------------------------|-----------------------------------|-----------------------|--------------------------|-----------------|----------------|----------------------|
| 2026-04-13 10:15:00  | 8f3a...    | J. Pérez    | Ajuste cálculo BEG para cohortes egresadas   | beg_engine.py, export/            | Requerimiento científico | Mejora trazabilidad     | datos_2026.csv  | v2.1.0         | Validado por QA      |

## Entradas Unificadas de Cambios (marzo 2026)

| Fecha                | run_id / Responsable | Descripción resumida                                                                                                    | Archivos afectados                                 | Validación / Observaciones                |
|----------------------|---------------------|------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------|-------------------------------------------|
| 2026-03-11           | -                   | Homologación y trazabilidad robusta de cohortes, niveles y RA. Simulación ajustada a 35 estudiantes/cohorte.            | matric, perfil_logro, ra_logro_individual.csv, etc.| Exports generados con trazabilidad total. |
| 2026-03-11           | -                   | Corrección de error de variable no definida (`full_matrix`) en exportación de matriz de logros.                         | ra_logro_matrix.csv                                | Motivo y solución documentados.           |
| 2026-03-11           | -                   | Pendiente menor: error en BEG_ISPG (comparación string/int), no afecta exports principales.                             | beg_engine.py, ispg_engine.py                      | Listo para commit y push.                 |
| 2026-03-23           | GitHub Copilot      | Corrección: el campo `Nivel` en todos los exports refleja el nivel académico real alcanzado por el estudiante.          | ra_logro_individual.csv, competencia_logro_individual.csv, perfil_logro_individual.csv, riesgos_internos_individual.csv | Validado, sin errores de sintaxis.        |
| 2026-03-24           | -                   | Simulador ajustado: al menos 20 estudiantes por nivel máximo, progresión estricta, datos generados y verificados.      | simulador, datos simulados                         | Progresión y datos coherentes.            |
| 2026-03-24           | -                   | Análisis de exportaciones: seguimiento longitudinal, cálculo de logros, trazabilidad y progresión académica real.       | ra_logro_individual.csv, competencia_logro_individual.csv, perfil_logro_individual.csv, ra_logro_matrix.csv             | Cumple requisitos SSD.                    |
| 2026-03-24           | -                   | Explicación de perfiles elevados en primer nivel y descripción de ra_logro_matrix.csv para análisis y visualización.     | ra_logro_matrix.csv                                | Documentación ampliada.                   |

---

## Control de Versiones y Auditoría

- Todos los cambios anteriores están respaldados en el sistema de control de versiones (Git) y documentados en esta bitácora.
- Cada entrada resume los cambios, responsables y validaciones realizadas.
- Para detalles completos, consultar los archivos originales de bitácora de cambios de cada fecha.

---

Este archivo debe ser actualizado y revisado periódicamente para mantener la integridad científica y operativa del SSD Curricular.
