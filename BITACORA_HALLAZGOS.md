# Bitácora de hallazgos — pipeline del modelo nuevo

**Fecha:** 2026-06-22
**Rama:** `feat/streamlit-simulador` (basada en `origin/simulador`)
**Estado:**
- Hallazgo 1 (orden lectura/escritura) → **CORREGIDO** (aprobado por Cynthia).
- Hallazgo 2 (índice no único en el mapeo, enmascarado por el 1) → **CORREGIDO** (aprobado por Cynthia).
- Hallazgo 3 (selección de cohortes para el riesgo externo global) → **CORREGIDO** (aprobado por Cynthia con la lógica correcta: promedio por períodos con datos, no por cohortes).
- Hallazgo 5 (perfiles idénticos en períodos con un solo RA) → **NO es un bug; escasez de datos.** Decisión de modelado **pendiente de Cynthia**.

Este registro documenta un bug **pre-existente** en `main.py` que salió a la luz al
poder ejecutar por primera vez el pipeline completo del modelo nuevo. En la rama
`origin/simulador` el pipeline no llegaba a correr porque faltaban los módulos de
exportación (`ssd_core/export/`); al agregarse los stubs, `main.py` ya ejecuta y el
problema queda expuesto.

**Importante:** el bug NO fue introducido por la adaptación de la interfaz. Los
cambios de la interfaz (parametrización por variable de entorno + cableado) pasaron
la prueba de no-regresión byte a byte. El bug vive en la lógica de exportación de
`main.py`, que no se tocó.

---

## Hallazgo: `riesgos_externos_individual.csv` no se genera (orden lectura/escritura)

### Síntoma observable
En una corrida limpia del pipeline:
- **No se genera** `export/riesgos_externos_individual.csv`.
- La columna **`Riesgo_externo` queda en `0`** para todas las cohortes en
  `export/BEG_ISPG_M.csv`.

### Causa raíz (técnica)
En `main.py` (raíz de la rama `simulador`):

1. Alrededor de la **línea ~320**, el script **lee** el archivo de riesgos externos
   usando el `run_id` de la corrida **actual**:
   ```python
   riesgos_ext_path = f'export/riesgos_externos_{run_id}.csv'
   if os.path.exists(riesgos_ext_path):
       riesgos_ext = pd.read_csv(riesgos_ext_path)
       ...
       riesgos_ext.to_csv('export/riesgos_externos_individual.csv', index=False)
   ```
2. Pero ese archivo **se escribe más abajo**, alrededor de la **línea ~344**:
   ```python
   export_engine = ExportEngine(export_dir)
   export_engine.export(riesgos_internos, f'riesgos_internos_{run_id}.csv')
   export_engine.export(riesgos_externos, f'riesgos_externos_{run_id}.csv')
   ```
3. El `run_id` se genera fresco en cada corrida (`audit_trail.register(...)`, línea
   ~88), así que el archivo `riesgos_externos_{run_id}.csv` **todavía no existe** en
   el momento de la lectura (línea ~320). El `if os.path.exists(...)` da `False`, el
   bloque se salta, y `riesgos_externos_individual.csv` nunca se crea.

En resumen: **se lee en la línea ~320 algo que recién se escribe en la línea ~344.**
La lectura ocurre antes que la escritura, con el mismo `run_id`.

### Por qué importa (efecto en el indicador ISPG)
El ISPG se calcula como:

```
ISPG = 0.50 · BEG − 0.30 · Riesgo_interno − 0.20 · Riesgo_externo
```

Si `Riesgo_externo` queda en `0`, el término `− 0.20 · Riesgo_externo` desaparece y
el **ISPG sale más alto de lo que debería**. Es un indicador central de la tesis, así
que el efecto es académicamente relevante, no cosmético.

### Lo que SÍ funciona (descarta otras causas)
- El upstream está bien: `simular_riesgos.py` identificó **76 egresados** (llegan a
  NOVENO y nunca desertaron) y escribió `ssd_core/config/riesgos_externos.csv`
  correctamente, con empleabilidad y satisfacción por estudiante.
- Los stubs de exportación funcionan: `export/riesgos_externos_{run_id}.csv` **sí se
  escribe** (línea ~344), solo que después de que se lo necesita.

### Corrección aplicada (aprobada por Cynthia)
Se aplicó la opción (A): se movió la escritura de `export/riesgos_externos_{run_id}.csv`
a **antes** del bloque de lectura (instanciando `ExportEngine(export_dir)` inline, porque
`export_engine` se define más abajo). Verificado: el bloque de lectura ya se ejecuta.

---

## Hallazgo 2: índice no único en el mapeo de trazabilidad (enmascarado por el 1)

### Síntoma
Al corregir el hallazgo 1, el bloque de lectura por fin se ejecutó y `main.py`
**se cayó** con `InvalidIndexError: Reindexing only valid with uniquely valued Index objects`.

### Causa raíz
El bloque hacía:
```python
perfil_idx = perfil_logro.set_index('ID_EST')
riesgos_ext['ID_Cohorte'] = riesgos_ext['estudiante_id'].map(perfil_idx['ID_Cohorte'])
```
`perfil_logro_individual.csv` tiene **muchas filas por estudiante** (~60: una por
perfil/periodo), así que `set_index('ID_EST')` produce un índice **no único** y `.map()`
sobre ese índice falla. El bug estaba **enmascarado** por el hallazgo 1: como el bloque
nunca se ejecutaba, nunca se disparaba.

### Corrección aplicada (aprobada por Cynthia)
**No** se deduplican filas. Se **agrupa por `ID_Cohorte` (grupo) e `ID_EST` (individual)**:
```python
perfil_grp = perfil_logro.groupby(['ID_Cohorte', 'ID_EST'], as_index=False).first()
riesgos_ext['ID_Cohorte'] = riesgos_ext['estudiante_id'].map(perfil_grp.set_index('ID_EST')['ID_Cohorte'])
```
Criterio de Cynthia: los estudiantes se agrupan por las variables que se repiten en
todos los procesos — `ID_EST` para análisis individuales, `ID_Cohorte` para análisis
por grupos, `PERIODO` para revisión temporal. Verificado: `riesgos_externos_individual.csv`
se genera con `ID_Cohorte` y `Fecha_corte` correctos (ej. `E12 → O2018-1`).

---

## Hallazgo 3: el riesgo externo global usa cohortes sin egresados (CORREGIDO)

### Síntoma
Aun con los hallazgos 1 y 2 corregidos, **`Riesgo_externo` sigue en `0`** en
`export/BEG_ISPG_M.csv` para todas las cohortes.

### Causa raíz
El `Riesgo_externo` de la tabla de indicadores **no proviene** del archivo individual que
se arregló, sino del cálculo del indicador en `calcular_ispg.py` (línea ~146) y, de forma
idéntica, en `main.py` (línea ~543):
```python
cohortes_ordenadas = sorted(resumen_df['ID_Cohorte'].unique(), reverse=True)
cohortes_ultimos_5 = cohortes_ordenadas[:5]   # las 5 cohortes MÁS RECIENTES de todas
valores_ultimos_5 = riesgos_ext[riesgos_ext['ID_Cohorte'].isin(cohortes_ultimos_5)]['riesgo_externo']
riesgo_ext_global = np.median(valores_ultimos_5) if len(valores_ultimos_5) > 0 else np.nan
```
El "riesgo externo global" se calcula como la mediana de **las 5 cohortes más recientes**
(`O2025-2, O2025-1, O2024-2, O2024-1, O2023-2`). Pero el riesgo externo
(empleabilidad/satisfacción) **solo existe para egresados**, que están en las cohortes
**viejas** (2018-1 … 2022-1). Las 5 más recientes **no tienen egresados**, así que
`valores_ultimos_5` queda vacío → `riesgo_ext_global = nan` → `Riesgo_externo = 0`.

Confirmado con datos: las 9 cohortes con egresados (2018-1…2022-1) **no se solapan** con
las 5 que el cálculo considera "recientes".

### Efecto en la tesis
Mismo efecto que el hallazgo 1 sobre el ISPG: con `Riesgo_externo = 0` el término
`− 0.20 · Riesgo_externo` desaparece y el **ISPG sale más alto de lo que debería**.

### Corrección aplicada (aprobada por Cynthia)
Cynthia aclaró la lógica correcta: **el riesgo externo NO se promedia por cohortes**, sino
que se calcula como el **promedio de los últimos 5 períodos con datos reales** que existen
en el archivo de riesgo externo. Si un período no tiene datos, no se incluye; si hay menos
de 5 períodos con datos, se usan los que existan.

El cálculo se reemplazó en `calcular_ispg.py` (línea ~144) y, de forma idéntica, en
`main.py` (línea ~541):
```python
# antes: las 5 cohortes más recientes (sin egresados) → vacío → 0
periodos_con_datos = sorted(riesgos_ext.loc[riesgos_ext['riesgo_externo'].notna(), 'Periodo'].unique())
periodos_ultimos_5 = periodos_con_datos[-5:]
valores_ultimos_5 = riesgos_ext[riesgos_ext['Periodo'].isin(periodos_ultimos_5)]['riesgo_externo'].dropna()
riesgo_ext_global = float(np.mean(valores_ultimos_5))   # promedio, según criterio de Cynthia
```
Cambios respecto al original: (1) la selección pasa de `ID_Cohorte` a la columna `Periodo`
de los datos de riesgo externo, tomando **solo períodos con datos**; (2) la agregación pasa
de `np.median` a `np.mean` (**promedio**, confirmado por Cynthia).

**Verificado tras la corrección:** corrida limpia del pipeline completo → `Riesgo_externo`
ya **no sale en `0`** en `export/BEG_ISPG_M.csv`. Con los datos actuales (único período con
datos = `2026-2`, 80 registros de egresados) el promedio es **78.207** para las 9 cohortes
con BEG definido, y coincide con el cálculo manual de control.

---

## Hallazgo 5: perfiles idénticos en períodos con un solo RA (NO es bug — escasez de datos)

### Contexto
Surge al verificar el fix del `Logro_Perfil` por competencia (commit `3823208`: mapeo real
RA→competencia desde `ra_competencia.csv` + promedio ponderado por `peso` de
`competencia_perfil.csv`). El fix corrige el bug previo en que `Logro_Perfil` salía
**replicado e idéntico en P1–P12** para todos los estudiantes y períodos.

### Síntoma observable
Tras el fix, en `export/perfil_logro_individual.csv`, un estudiante puede mostrar perfiles
**diferenciados** en unos períodos y **todos iguales** en otro. Ejemplo real (E1):

| Período | RA con datos | Competencias con dato | Perfiles P1–P12 |
|---|---|---|---|
| 2018-1 | 5 RA | 3 comps | **diferenciados** (60.07–62.63) |
| 2018-2 | 5 RA | 3 comps | **diferenciados** (59.45–65.10) |
| 2019-1 | **1 RA** (RA5=56) | **1 comp** (56.0) | **todos 56.0** |

### Causa raíz (NO es un bug del fix)
Es **escasez de datos**, no lógica defectuosa. La cadena en 2019-1:

```
1 RA (RA5 = 56)  →  1 competencia con dato (= 56.0)  →  los 12 perfiles = 56.0
```

Cuando solo hay datos para **una** competencia, cada perfil que la incluye calcula un promedio
ponderado sobre **un único valor** → devuelve ese valor (56.0) sin importar el `peso`. Si esa
competencia pertenece a los 12 perfiles, los 12 reportan 56.0.

Esto es **cualitativamente distinto** del bug viejo: aquel daba valores idénticos **aun con
datos ricos** (5 RA / 3 comps) porque el filtro RA→competencia usaba `asig` (sin `ID_COMP`) y
tomaba todos los RA. El fix lo demuestra: con 5 RA / 3 comps los perfiles **sí se diferencian**;
el `56.0` uniforme solo aparece cuando el período tiene un único RA registrado.

### Efecto / caveat de modelado
Cuando un perfil se calcula con **una sola** de las competencias que lo componen, el
`Logro_Perfil` reporta el valor de esa única competencia como si fuera todo el perfil →
**sobre-representa** con cobertura parcial.

### Decisión PENDIENTE de Cynthia (3 opciones)
1. **Umbral de cobertura mínima:** no emitir `Logro_Perfil` si faltan datos para un % de las
   competencias del perfil (p. ej. < 50% de cobertura).
2. **Columna de cobertura:** añadir `n_comps_con_dato / n_comps_perfil` para que Power BI pueda
   filtrar o ponderar la confianza del valor.
3. **Dejarlo como está:** aceptar "logro parcial con los datos disponibles".

No se aplica ningún cambio de código hasta que Cynthia decida.
