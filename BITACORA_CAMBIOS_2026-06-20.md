# Bitácora de Cambios Recientes

**Fecha:** 2026-06-20
**Rama:** `feat/interfaz-streamlit`
**Tipo:** análisis (no se modificó el modelo ni los datos versionados)

## Motivo
Cynthia preguntó por qué la cantidad de graduados "bajó" de 280 a 96. Este
registro deja por escrito **por qué la comparación real es 105 contra 96, y no
280 contra 96**, con los números medidos del propio simulador.

## Conclusión central: nunca hubo 280 graduables

Los 280 estudiantes = **8 cohortes × 35**. Pero por el **diseño de
"envejecimiento de cohortes"** del modelo (no por la regla de repeticiones), a
cada cohorte se le fija su `Max_nivel` al crearla, según su antigüedad dentro de
la ventana de 8 años:

| Cohortes | Antigüedad | `Max_nivel` asignado | ¿Pueden llegar a NOVENO? |
|---|---|---|---|
| 2019, 2020, 2021 (105 est.) | ≥5 años | **NOVENO** | **Sí** |
| 2022, 2023 (70 est.) | 3–4 años | TERCERO…OCTAVO | No (por diseño) |
| 2024, 2025, 2026 (105 est.) | ≤2 años | PRIMER/SEGUNDO/TERCERO | No (por diseño) |

Verificado en los datos generados: **todos** los que llegan a NOVENO salen solo
de las cohortes 2019/2020/2021. Las otras 5 cohortes (175 estudiantes) son, a
propósito, estudiantes de primeros o medios niveles — **nunca iban a graduarse
en esta ventana, con o sin regla de repeticiones**.

Por lo tanto, la comparación honesta no es 280 → 96, sino **105 → 96**.

## 1. Por categoría: cuántos llegan a NOVENO (promedio sobre 280)

| Categoría | Total ≈ | Llegan a NOVENO ≈ |
|---|---|---|
| `sin_repeticion` | 196 | 74 |
| `repite_leve` | 56 | 21 |
| `repite_maximo_pasa` | 6 | 2 |
| `pierde_carrera` | 22 | 0 |
| **Total NOVENO** | | **≈ 96** |

`repite_leve` y `repite_maximo_pasa` **sí se gradúan** (aprueban tras repetir).
Lo único que saca a un estudiante de NOVENO es `pierde_carrera`, porque a esos su
`Max_nivel` se reescribe a SEGUNDO/TERCERO/CUARTO. Los ~74 + 21 + 2 que llegan
son exactamente los de cohortes maduras que **no** cayeron en `pierde_carrera`.

## 2. De los que NO llegan a NOVENO (280 − 96 = 184), ¿por qué?

- **~175 → por cohorte demasiado reciente** (2022–2026). No son fracasos: son
  estudiantes a medio camino o de primer nivel por diseño.
- **~9 → `pierde_carrera`** que cayeron en una cohorte madura (de los 22 totales,
  ~37 % caen en cohortes maduras).
- **0 → por "quedarse sin tiempo dentro de la ventana de 8 años".** Ese mecanismo
  **no existe** en el modelo: el simulador vuelve a generar *todos* los niveles
  cada año, así que un estudiante de cohorte NOVENO alcanza NOVENO ya en su primer
  año simulado. La ventana de 8 años no corta a nadie a mitad de avance.

## 3. Graduados en la versión original (sin ninguna regla)

Medido corriendo el simulador real con `SSD_P_REPITE=0`: **105 graduados,
exactos y estables en 5 corridas** (= las 3 cohortes maduras completas).

## La diferencia real, en una línea

**105 → ~96.** La caída de ~9 graduados es **íntegramente** la categoría
`pierde_carrera` (8 % del total) en la porción que cayó en cohortes maduras. No
hay pérdida por tiempo ni por abandono.

## Cómo se midió (reproducible)

- Conteo de NOVENO con nota sobre `ssd_core/config/matriculacion_historica_test.csv`.
- Escenario "sin regla": simulador real con `SSD_P_REPITE=0`,
  `SSD_P_REPITE_MAXIMO=0`, `SSD_P_PIERDE_CARRERA=0` (5 corridas → 105 estable).
- Desglose por categoría: réplica fiel de la asignación de categorías del modelo,
  validada contra el simulador real (media de NOVENO = 96.8; corridas reales ≈ 95–96).
- Los datos versionados se restauraron con `git checkout` tras cada medición; el
  modelo no se modificó.

---

**Nota:** quedan dos puntos abiertos a la espera de la decisión de Cynthia; no se
abordan en este análisis.
