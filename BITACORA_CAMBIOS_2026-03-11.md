# Bitácora de Cambios Recientes

**Fecha:** 2026-03-11

## Cambios realizados desde el último guardado:

1. **Homologación y trazabilidad robusta:**
   - Todos los datos de trazabilidad (ID_Cohorte, Nivel, Periodo, Fecha_matriculacion, Fecha_carga) para los estudiantes ahora se obtienen directamente de la tabla de matriculación histórica (`matric`), garantizando unicidad y consistencia.
   - Se eliminó el mapeo desde `perfil_logro` para evitar errores de índice no único.

2. **Homologación de variables clave:**
   - Se homologó `ra_id` a `RA_ID` y luego a `ID_RA` en el flujo de datos para compatibilidad con los engines y los exports.
   - Se agregó la columna `RA_ID` a los exports de RA para trazabilidad.

3. **Simulación ajustada:**
   - Se modificó la simulación para generar **35 estudiantes por cohorte** en vez de 80.
   - Se ejecutó la simulación y se regeneraron los datos históricos.

4. **Procesamiento principal actualizado:**
   - Se ejecutó el flujo principal con los nuevos datos simulados.
   - Todos los archivos de exportación (`ra_logro_individual.csv`, `competencia_logro_individual.csv`, `perfil_logro_individual.csv`, `riesgos_internos_individual.csv`, etc.) se generaron correctamente y con trazabilidad completa.

5. **Corrección de errores y robustez:**
   - Se corrigió un error de variable no definida (`full_matrix`) en la exportación de la matriz de logros.
   - Se documentó y explicó el motivo de los errores de índice y cómo se resolvieron sin afectar los cálculos.

6. **Pendiente menor:**
   - Queda un error menor en el análisis BEG_ISPG (comparación entre string e int), que no afecta los exports principales.

---

**Listo para commit y push a GitHub.**
