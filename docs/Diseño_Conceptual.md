# Informe SSD Curricular - Diseño y Especificaciones

## 1. Concepto General

El Sistema de Soporte a la Decisión (SSD) curricular es una plataforma modular para el aseguramiento de la calidad académica en educación superior. Permite evaluar, auditar y mejorar el diseño curricular de múltiples carreras, integrando datos internos y externos, riesgos, indicadores y trazabilidad.

## 2. Objetivos
- Aseguramiento de calidad curricular multicarrera.
- Trazabilidad, auditoría y reproducibilidad total.
- Integración con sistemas académicos externos (ACTUA).
- Flexibilidad y extensibilidad para nuevas reglas, motores y análisis.

## 3. Arquitectura Modular

```
ssd_core/
│
├── config/
│   ├── model_config.yaml
│   ├── ra_competencia.csv
│   ├── competencia_perfil.csv
│   ├── carreras.csv
│   ├── riesgos_internos.csv
│   ├── riesgos_externos.csv
│
├── data/
│   ├── raw/
│   ├── processed/
│
├── engines/
│   ├── normalizacion_engine.py
│   ├── ra_engine.py
│   ├── competencia_engine.py
│   ├── perfil_engine.py
│   ├── external_risk_engine.py
│   ├── internal_risk_engine.py
│   ├── beg_engine.py
│   ├── ispg_engine.py
│
├── validation/
│   ├── cronbach.py
│   ├── sensibilidad.py
│   ├── montecarlo.py
│
├── audit/
│   ├── audit_trail.py
│   ├── version_control.py
│
├── export/
│   ├── powerbi_export.py
│
├── simulation/
│   ├── run_example.py
│
└── main.py
```

## 4. Metodología y Modelo Matemático

### Jerarquía Curricular
- RA (Resultados de Aprendizaje) → Competencia → Perfil de Egreso

### Modelo No Compensatorio
- Cada competencia depende del RA más débil (mínimo cumplimiento relativo).
- No hay compensación entre RA.
- Se registra el RA limitante.

### Motores de Riesgo
- Riesgos internos: desempeño, repitencia, deserción, brechas.
- Riesgos externos: empleabilidad, satisfacción, contexto socioeconómico.
- BEG: Brecha estructural de egreso.
- ISPG: Indicador sintético de progreso global.

### Validaciones
- Integridad de RA y competencias.
- Validación de mínimos y pesos.
- Alertas si faltan datos o hay inconsistencias.
- Validación estadística: Cronbach, sensibilidad, Monte Carlo.

## 5. Requisitos
- Modularidad total.
- Configuración 100% en archivos (sin hardcode).
- Multicarrera y multiusuario.
- Integración nativa de riesgos, BEG, ISPG.
- Auditoría robusta (run_id, hash, versión, timestamp).
- Exportación lista para Power BI y ACTUA.
- Simulación de datos para pruebas (`run_example.py`).

## 6. Flujo de Ejecución
1. Usuario sube archivos de datos y configuración.
2. Ejecuta el sistema (`python main.py --carrera_id=...`).
3. El sistema normaliza, valida y calcula RA, competencias, perfil, riesgos, BEG, ISPG.
4. Se generan outputs, alertas y auditoría.
5. Resultados exportados para análisis y visualización.

## 7. Diseño de Clases
- `ConfigLoader`: carga y valida configuración.
- `DataLoader`: carga y normaliza datos.
- `RAEngine`: calcula RA por estudiante.
- `CompetenciaEngine`: calcula competencias (no compensatorio).
- `PerfilEngine`: calcula perfil de egreso.
- `ExternalRiskEngine` / `InternalRiskEngine`: calculan riesgos.
- `BEGEngine`: calcula brecha estructural.
- `ISPGEngine`: calcula indicador sintético global.
- `ValidationEngine`: ejecuta validaciones y alertas.
- `AuditTrail`: registra run_id, hash, versión, timestamp.
- `ExportEngine`: exporta resultados.
- `SimulationEngine`: genera datos simulados (`run_example.py`).
- `SSDRunner`: orquestador principal.

## 8. Ejemplo de Configuración de Riesgos
```yaml
riesgos:
  internos:
    - archivo: riesgos_internos.csv
      columnas: [desempeño, repitencia, deserción]
  externos:
    - archivo: riesgos_externos.csv
      columnas: [empleabilidad, satisfacción]
```
