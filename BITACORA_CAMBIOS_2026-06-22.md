# Bitácora de cambios — 2026-06-22

**Rama:** `feat/streamlit-simulador` (creada desde `origin/simulador`)
**Objetivo:** adaptar la interfaz Streamlit al **modelo nuevo de Cynthia** (simulador
longitudinal de `origin/simulador`), sin tocar el modelo académico.
**Estado git:** todo en rama local, **sin push ni merge** (regla 4 de CLAUDE.md).

---

## Contexto
Cynthia subió `origin/simulador` con una reescritura completa del simulador a un modelo
longitudinal real (reloj semestre a semestre, prerrequisitos, notas por capacidad, regla
de 3 reprobaciones, graduación = aprobar toda la malla). Confirmó que quiere la interfaz
adaptada a ESE modelo, no al anterior. Esta rama hace esa adaptación.

## Cambios realizados

### Frente 1 — Stubs de exportación (`aa1719e`)
- Se agregaron `ssd_core/export/{__init__,powerbi_export,advanced_export}.py`.
- Su `main.py` los importaba (`ExportEngine`, `export_advanced`) pero **faltaban** en la
  rama `simulador`, así que el pipeline nunca había podido ejecutarse. Con los stubs, corre.
- Firmas compatibles con el uso real: `ExportEngine(dir).export(data, file)` y
  `export_advanced(results, dir, file)`.
- Se forzó el `git add` porque `.gitignore` ignora `ssd_core/export/`; es código fuente y
  debe versionarse.

### Frente 2 — Interfaz adaptada (`5199186`, `297256a`)
- `app.py`: el paso 3 del pipeline apunta a `main.py` en la raíz (en la rama `simulador`
  `main.py` se movió fuera de `ssd_core/`).
- Panel de parámetros del modelo nuevo: **año de inicio y año de fin como campos
  separados**, estudiantes por cohorte y máximo de materias por semestre.
- Se quitaron los controles/variables de entorno del modelo viejo que este simulador ignoraba.
- Se conserva el botón "Exportar para Power BI" (esquema estrella verificado: las 3
  dimensiones y los hechos existen con los mismos nombres).
- Se agregó una **nota visible** recordando que copiar los datos simulados a
  `ssd_core/config/` es un **paso manual** (decisión de Cynthia; la UI no lo automatiza).

### Frente 3 — Parametrización del simulador (`2a2ef47`)
- En `simular_matriculacion.py` se levantaron a variable de entorno, con **default = valor
  original del modelo**:
  - `SSD_ANIO_INICIO` / `SSD_ANIO_FIN` (ventana 2018–2026)
  - `SSD_N_ESTUDIANTES_COHORTE` (25)
  - `SSD_MAX_MATERIAS_SEMESTRE` (6)
- El corte de ingreso de cohortes se ató a `ANIO_FIN - 1` (antes literal `2025`), para que
  se mueva con el parámetro en vez de quedar fijo.
- **No** se tocaron fórmulas, lógica del modelo ni la **trazabilidad** (`Fecha_matriculacion`,
  `Fecha_carga`, `Periodo`, etc. — estándar de calidad de datos de Cynthia).
- **No-regresión verificada byte a byte**: con los defaults y semilla fija, la salida del
  simulador es idéntica a la de `origin/simulador` (mismo sha256).

### Correcciones aprobadas en `main.py` (`3e3804d`)
Dos bugs **pre-existentes** del pipeline de riesgos externos, que salieron a la luz al
poder ejecutar el pipeline por primera vez. Aprobados por Cynthia (ver `BITACORA_HALLAZGOS.md`):
1. **Orden lectura/escritura:** se escribe `export/riesgos_externos_{run_id}.csv` antes de
   leerlo. Antes la lectura siempre fallaba y `riesgos_externos_individual.csv` no se generaba.
2. **Mapeo por agrupación (no deduplicación):** se agrupa por `ID_Cohorte` e `ID_EST` para
   evitar el `InvalidIndexError` por índice no único.
- Verificado: el pipeline corre completo y `riesgos_externos_individual.csv` se genera con
  `ID_Cohorte` y `Fecha_corte` correctos.

### Corrección del Hallazgo 3 — riesgo externo por períodos (aprobada por Cynthia)
- En `calcular_ispg.py` (~línea 144) y `main.py` (~línea 541) se reemplazó el cálculo del
  **riesgo externo global**: antes tomaba "las 5 cohortes más recientes" (sin egresados →
  vacío → `0`). Ahora calcula el **promedio (`np.mean`) de los últimos 5 períodos con datos
  reales**, seleccionando por la columna `Periodo` del archivo de riesgo externo y usando
  solo los períodos que tienen datos (si hay menos de 5, los que existan).
- Confirmado por Cynthia: la agregación es **promedio**, no mediana; y la selección es por
  **período**, no por cohorte.
- **Verificado:** corrida limpia del pipeline → `Riesgo_externo` ya **no sale en `0`** en
  `export/BEG_ISPG_M.csv` (78.207 con los datos actuales). Detalle en `BITACORA_HALLAZGOS.md`.

### Corrección de la fórmula del ISPG → Salud del sistema (aprobada por Cynthia)
- Cynthia corrigió la fórmula del ISPG. La anterior era una **resta** ponderada
  (`0.50·BEG − 0.30·Riesgo_interno − 0.20·Riesgo_externo`). La **correcta** es una
  **suma** ponderada y un complemento a 100:
  ```
  ISPG_raw      = 0.50·BEG + 0.30·Riesgo_interno + 0.20·Riesgo_externo
  Salud_sistema = 100 − ISPG_raw
  ```
- El campo que se guarda como `ISPG` en `export/BEG_ISPG_M.csv` ahora es
  **`Salud_sistema`** (el `100 − ISPG_raw`), no el `ISPG_raw`.
- Las **tres variables se usan en escala 0-100**. En `calcular_ispg.py` ya lo estaban.
  En el **bloque gemelo de `main.py`** se alineó la escala: se reescalan los riesgos a
  0-100 (igual que `calcular_ispg.py`) y se usa `BEG` directo (antes dividía `BEG/100` y
  clasificaba en 0-1); ahora clasifica en 0-100 con umbrales 75/60, idéntico al otro archivo.
- Pesos sin cambio: BEG 0.50, Riesgo_interno 0.30, Riesgo_externo 0.20.
- **Verificado** con corrida limpia del pipeline completo. `Salud_sistema` para las 9
  cohortes con egresados queda en **~65.8 – 67.2** (todas **Amarillo**); ejemplo
  `O2018-1`: BEG 19.65, R_int 26.047, R_ext 77.297 → ISPG_raw 33.099 → **Salud 66.902**.
  (Con la fórmula anterior de resta el ISPG salía negativo para estas cohortes.)

### Documentación (`fff1d64`, `5b3912b`)
- `BITACORA_HALLAZGOS.md`: registro técnico de los 3 hallazgos (los 3 corregidos y verificados).

## Cómo correr la interfaz (Mac)
```
python3 -m pip install streamlit
python3 -m streamlit run app.py
```
