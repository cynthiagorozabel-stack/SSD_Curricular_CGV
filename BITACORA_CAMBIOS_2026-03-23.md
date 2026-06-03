# Bitácora de Cambios - Corrección de Nivel Real en Exportaciones

**Fecha:** 2026-03-23
**Responsable:** GitHub Copilot

## Objetivo
Asegurar que el campo `Nivel` en todos los archivos de exportación refleje el nivel académico real alcanzado por el estudiante, basado en la asignatura o RA correspondiente, y no el nivel de cohorte ni el primer registro.

## Cambios Realizados

### 1. Exportación de RA (ra_logro_individual.csv)
- El campo `Nivel` ya reflejaba el nivel real de la asignatura asociada a cada RA usando el mapeo desde `asignaturas.csv`.

### 2. Exportación de Competencias (competencia_logro_individual.csv)
- Se modificó la lógica para que el campo `Nivel` sea el nivel más alto de los RA asociados a la competencia para cada estudiante.
- Se utiliza un diccionario de orden lógico de niveles para determinar el máximo.

### 3. Exportación de Perfiles (perfil_logro_individual.csv)
- Se corrigió la asignación de `Nivel` para que sea el nivel más alto de las asignaturas cursadas por el estudiante en cada periodo.
- Se eliminó la dependencia del primer registro o cohorte.

### 4. Exportación de Riesgos Internos (riesgos_internos_individual.csv)
- Se reemplazó el mapeo de cohorte por el nivel máximo real alcanzado por cada estudiante en la historia de matriculación.

## Lógica Implementada
- Se utiliza el campo `NIVEL` de `asignaturas.csv` y de la historia de matriculación para determinar el nivel real.
- Se emplea un diccionario de orden de niveles para comparar y seleccionar el nivel más alto.
- Se asegura la deduplicación de notas por RA y estudiante antes de calcular logros.

## Validación
- Se revisó que no existan errores de sintaxis tras los cambios.
- Se recomienda ejecutar el script principal y revisar los archivos de exportación para validar que el campo `Nivel` es coherente con el avance académico real.

## Observaciones
- Todos los cálculos y exportaciones ahora reflejan el nivel real alcanzado por el estudiante, eliminando inconsistencias previas.
- Se mantiene la trazabilidad de cohortes y periodos para otros fines analíticos.

---
