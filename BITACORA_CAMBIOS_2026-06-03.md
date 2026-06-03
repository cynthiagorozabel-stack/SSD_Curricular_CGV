# Bitácora de Cambios Recientes

**Fecha:** 2026-06-03
**Rama:** `fix/rendimiento-7-anios`

## Objetivo
Reducir el rango de simulación (antes 17 años fijos) y acelerar la ejecución, sin
alterar la lógica de cálculo de los indicadores ni el modelo de gestión.

## Cambios realizados

1. **Rango de simulación parametrizado (un solo parámetro):**
   - En `ssd_core/simulation/simular_matriculacion.py` se reemplazó el rango calendario
     fijo `range(2010, 2027)` por un único parámetro **`N_ANIOS_SIMULACION = 8`** (valor
     óptimo elegido), anclado a `ANIO_FINAL = 2026`. Para cambiar el rango (por ejemplo a
     7) basta con editar esa línea.
   - La clasificación de cohortes (graduada / intermedia / reciente) pasó a ser **relativa
     a la antigüedad** dentro de la ventana (≥5 años → graduada/NOVENO; ≤2 → reciente;
     resto → intermedia), de modo que las cohortes más antiguas siguen graduándose y
     BEG/ISPG/riesgos externos se siguen calculando para cualquier N.

2. **Corrección de esquema en el simulador de riesgos:**
   - `ssd_core/simulation/simular_riesgos.py` escribía `riesgos_externos.csv` con columnas
     `ID_EST` y `satisfaccion` (sin tilde), incompatibles con el resto del sistema
     (`model_config.yaml`, `main.py`, `simular_matriculacion.py` usan `estudiante_id` y
     `satisfacción`). Se homologó el encabezado. Esto desbloquea el cálculo de BEG/ISPG.
   - Este simulador no define un rango de años propio: hereda la ventana del CSV de
     matriculación, por lo que queda alineado automáticamente con `N_ANIOS_SIMULACION`.

3. **Cálculo del ISPG en archivo aparte (`calcular_ispg.py`):**
   - `main.py` no generaba `BEG_ISPG_M.csv` por un bug pre-existente (comparación
     `'' > 1` cuando una cohorte aún no tiene graduados).
   - Se decidió **no modificar** el bloque de indicadores de `main.py`. En su lugar,
     `calcular_ispg.py` (en la raíz) reproduce idéntica la lógica BEG/ISPG (misma
     definición de BEG, misma fórmula `ISPG = 0.50·BEG − 0.30·R_int − 0.20·R_ext`, mismos
     pesos y umbrales) y calcula el ISPG **solo para las cohortes graduadas**. Genera
     `export/BEG_ISPG_M.csv`. Se ejecuta después de `main.py`.

4. **Datos simulados regenerados** a la ventana de 8 años (2019–2026).

## Pasos para ejecutar (desde la raíz del proyecto)
```bash
export PYTHONPATH=.          # en Windows PowerShell: $env:PYTHONPATH="."

# 1) Generar matriculación histórica (aquí se ajusta N_ANIOS_SIMULACION = 8 o 7)
python ssd_core/simulation/simular_matriculacion.py

# 2) Generar riesgos internos/externos (hereda la ventana de la matriculación)
python ssd_core/simulation/simular_riesgos.py

# 3) Pipeline de indicadores (usa los módulos de exportación Power BI locales)
python ssd_core/main.py

# 4) Calcular el ISPG por cohorte graduada -> export/BEG_ISPG_M.csv
python calcular_ispg.py
```

## Tiempo de ejecución (pipeline completo, medido en máquina de desarrollo)
| | Antes (17 años) | Después (8 años) |
|---|---|---|
| Total pipeline | 45,5 s | 10,7 s |
| Filas matriculación | 430.759 | ~96.000 |

**Mejora: ~4,2× más rápido.** El factor principal fue reducir el dataset ~4,5×.

## Alcance respetado
- No se modificó `main.py`, `engines/`, `validation/`, `base/`, `model_config.yaml` ni los
  CSV del modelo (RA, competencias, perfiles, pesos).
- Sin dependencias nuevas. Todo local y basado en CSV (offline).

## Observación (comportamiento pre-existente del modelo, no modificado)
El ISPG resulta negativo → "Rojo" porque `Riesgo_interno` mezcla `desempeño` (escala
0–100) con conteos de repitencia/deserción mientras BEG se escala a 0–1, y
`Riesgo_externo` queda en 0 porque el modelo toma las 5 cohortes más recientes (sin
graduados → sin dato externo). Son características previas de `main.py`; se replicaron tal
cual, sin tocar el modelo.

---

**Pendiente:** push / PR a confirmar por Cynthia (por ahora todo permanece local).
