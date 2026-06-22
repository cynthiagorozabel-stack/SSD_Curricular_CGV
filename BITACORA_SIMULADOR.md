# Bitácora de cambios — rama `simulador`

Generada: 2026-06-21

A continuación se listan los commits presentes en `origin/simulador` (hash, autor, fecha, mensaje y archivos modificados).

---

- **bff00b3** | cynthiagorozabel-stack | 2026-06-21
  - Mensaje: Edicion Simulacion 21 junio
  - Archivos modificados:
    - audit/audit_0f0f271f-ee76-4e7a-8a65-7ebb54485c0a.json
    - audit/audit_2023fe0d-9b43-43f6-a5ad-63690e1c1f1e.json
    - audit/audit_3959608d-b0f1-475d-8206-ff925239d40c.json
    - audit/audit_c469a62c-abde-497a-8b1b-77b1e3e7119b.json
    - audit/audit_d546a9b9-f8b1-48d7-a8a0-0aa554254506.json
    - audit/audit_d57187f7-b93d-445e-9435-b958a6a69b0a.json
    - audit/audit_d6221fc8-380c-49b9-a480-beeccd139fec.json
    - audit/audit_eb67a076-a7f7-4001-a424-fca59e64abae.json
    - calcular_ispg.py
    - export/BEG_ISPG_M.csv
    - export/alpha_cronbach_d57187f7-b93d-445e-9435-b958a6a69b0a.json
    - export/alpha_cronbach_fca83e77-1ed1-4030-a113-08ad3f9b96f5.json
    - export/competencia_logro_individual.csv
    - export/perfil_logro_individual.csv
    - export/perfil_promedio_individual.csv
    - export/ra_logro_individual.csv
    - export/ra_logro_matrix.csv
    - export/resultados_avanzados.csv
    - export/riesgos_externos_d57187f7-b93d-445e-9435-b958a6a69b0a.csv
    - export/riesgos_externos_fca83e77-1ed1-4030-a113-08ad3f9b96f5.csv
    - export/riesgos_internos_d57187f7-b93d-445e-9435-b958a6a69b0a.csv
    - export/riesgos_internos_fca83e77-1ed1-4030-a113-08ad3f9b96f5.csv
    - export/riesgos_internos_individual.csv
    - main.py
    - ssd_core/config/matriculacion_historica_test.csv
    - ssd_core/config/riesgos_externos.csv
    - ssd_core/config/riesgos_internos.csv
    - ssd_core/simulation/simular_matriculacion.py
    - ssd_core/simulation/simular_riesgos.py
    - ssd_core/simulation/ssd_core/config/matriculacion_historica_test.csv
    - ssd_core/simulation/ssd_core/config/riesgos_externos.csv
    - ssd_core/simulation/ssd_core/config/riesgos_internos.csv

- **c31bfb5** | cynthiagorozabel-stack | 2026-06-16
  - Mensaje: Guardando avances en simulador nueva rama
  - Archivos modificados: (varios `audit/`, `export/`, `calcular_ispg.py`, `main.py`, `ssd_core/config/...`, etc.)

- **ee0bfc2** | jots9 | 2026-06-03
  - Mensaje: Docs: bitácora 2026-06-03 con cambios y pasos de ejecución
  - Archivos: BITACORA_CAMBIOS_2026-06-03.md

- **ba06569** | jots9 | 2026-06-03
  - Mensaje: Add calcular_ispg.py: cálculo independiente del ISPG por cohorte graduada
  - Archivos: calcular_ispg.py

- **bc1c2e1** | jots9 | 2026-06-03
  - Mensaje: Regenerar datos simulados con ventana de 8 años (2019-2026)
  - Archivos: varios en `ssd_core/config` y `ssd_core/simulation` (matriculación y riesgos)

- **06fcbbc** | jots9 | 2026-06-03
  - Mensaje: Fix: homologar esquema de riesgos_externos en simular_riesgos.py
  - Archivos: ssd_core/simulation/simular_riesgos.py

- **23f29a4** | jots9 | 2026-06-03
  - Mensaje: Parametrizar rango de simulación a N_ANIOS_SIMULACION=8 (antes 17 años fijos)
  - Archivos: ssd_core/simulation/simular_matriculacion.py, ssd_core/simulation/simular_riesgos.py

- **e669064** | cynthiagorozabel-stack | 2026-03-11
  - Mensaje: Ajustes: simulación 35 estudiantes/cohorte, trazabilidad robusta, exports corregidos, bugfixes
  - Archivos: BITACORA_CAMBIOS_2026-03-11.md, `audit/`, `export/`, `ssd_core/config/*`, `ssd_core/main.py`, `ssd_core/simulation/*`

- **bf007d5** | cynthiagorozabel-stack | 2026-03-09
  - Mensaje: Actualización simulador: separación de archivos, variables únicas y contextuales, y cohorte en todos los archivos
  - Archivos: muchos `audit/`, `export/`, `ssd_core/config/*`, `ssd_core/main.py`, `ssd_core/simulation/*`

- **4877e42** | cynthiagorozabel-stack | 2026-03-05
  - Mensaje: Homologación de ID_COMP en archivos de configuración y código
  - Archivos: `audit/`, `export/`, `ssd_core/config/*`, `ssd_core/main.py`

- **5df8b8c** | cynthiagorozabel-stack | 2026-03-05
  - Mensaje: Actualización: exportación de alpha de Cronbach, homologación de ID_EST, mejoras en matrices de logros y riesgos. Documentación y auditoría actualizadas.
  - Archivos: `audit/`, `export/*`, `ssd_core/main.py`

- **13bcfaa** | cynthiagorozabel-stack | 2026-03-04
  - Mensaje: Exportaciones, riesgos y análisis BEG/ISPG/Cronbach actualizados
  - Archivos: MANUAL_USO_SSD_CURRICULAR.md, `docs/`, `export/`, `ssd_core/*`

- **95f6169** | cynthiagorozabel-stack | 2026-03-04
  - Mensaje: Simulación histórica completa, IDs homologados, pipeline ejecutado y resultados actualizados
  - Archivos: estructura base del proyecto y múltiples `ssd_core`/`config`/`export` archivos

- **2f525f8** | cynthiagorozabel-stack | 2026-02-21
  - Mensaje: Initial commit: SSD Curricular base structure, config, simulation, tests
  - Archivos: estructura inicial del repositorio

---

Notas:
- Los commits listados son los recuperados desde `origin/simulador`. Para detalles más finos (diffs por commit), puedo generar un listado expandido o exportar los `git show`/parches.

