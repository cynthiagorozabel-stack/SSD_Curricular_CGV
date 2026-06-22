# Bitácora de hallazgos — pipeline del modelo nuevo

**Fecha:** 2026-06-22
**Rama:** `feat/streamlit-simulador` (basada en `origin/simulador`)
**Estado:** hallazgo **señalado, NO corregido** (pendiente de decisión de Cynthia).

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

### Arreglo propuesto (NO aplicado)
Es un cambio de **una línea de orden**, sin tocar fórmulas ni el modelo académico.
Dos opciones equivalentes:
- **(A)** Mover la escritura `export_engine.export(riesgos_externos, f'riesgos_externos_{run_id}.csv')`
  **antes** del bloque de lectura (~línea 320).
- **(B)** En el bloque de lectura, usar directamente el DataFrame `riesgos_externos`
  ya en memoria (o `ssd_core/config/riesgos_externos.csv`) en vez del archivo
  `riesgos_externos_{run_id}.csv`.

**No se aplica** ninguna por ahora: toca el pipeline de cálculo de indicadores, así
que requiere el visto bueno de Cynthia (reglas 1 y 3 de CLAUDE.md).
