# app.py
# -----------------------------------------------------------------------------
# Interfaz Streamlit para el pipeline de simulación del SSD Curricular.
#
# Adaptada al modelo nuevo (rama simulador):
#   - Configurar la ventana de simulación (año de inicio / año de fin),
#     estudiantes por cohorte y máximo de materias por semestre.
#   - Botón "Arrancar análisis": corre el pipeline completo con esos parámetros.
#   - Botón "Exportar para Power BI": consolida los CSV de salida (hechos +
#     dimensiones) en una carpeta lista para importar en Power BI.
#   - Mensajes de confirmación al terminar.
#
# Los parámetros se inyectan al simulador por variable de entorno; el modelo usa
# su valor original como default, así que dejar los campos en su valor por
# defecto reproduce el comportamiento base del modelo.
#
# No incluye gráficos ni vista previa de datos: el análisis visual se hace en
# Power BI directamente con los archivos exportados.
#
# Uso:  python3 -m streamlit run app.py   (desde la raíz del proyecto)
# -----------------------------------------------------------------------------
import os
import shutil
import subprocess
import sys

import streamlit as st

ROOT = os.path.dirname(os.path.abspath(__file__))
EXPORT_DIR = os.path.join(ROOT, "export")
CONFIG_DIR = os.path.join(ROOT, "ssd_core", "config")
POWERBI_DIR = os.path.join(ROOT, "powerbi_export")

# Pasos del pipeline, en orden (rutas relativas a la raíz del proyecto).
PIPELINE = [
    ("Simular matriculación histórica", "ssd_core/simulation/simular_matriculacion.py"),
    ("Simular riesgos (internos/externos)", "ssd_core/simulation/simular_riesgos.py"),
    ("Calcular indicadores (main)", "main.py"),
    ("Calcular ISPG por cohorte", "calcular_ispg.py"),
]

# Archivos del esquema estrella a consolidar para Power BI.
#   Dimensiones (desde ssd_core/config) y hechos/resultados (desde export/).
DIMENSIONES = ["dim_ra.csv", "dim_asignatura.csv", "dim_competencia.csv"]
HECHOS = [
    "resultados_avanzados.csv",
    "ra_logro_matrix.csv",
    "BEG_ISPG_M.csv",
    "ra_logro_individual.csv",
    "competencia_logro_individual.csv",
    "perfil_logro_individual.csv",
    "perfil_promedio_individual.csv",
    "riesgos_internos_individual.csv",
    "riesgos_externos_individual.csv",
]


def correr_pipeline(anio_inicio, anio_fin, n_estudiantes, max_materias):
    """Ejecuta los 4 scripts en orden con los parámetros indicados.

    Los parámetros se pasan al simulador por variable de entorno; el modelo usa
    su valor original como default. Devuelve (ok, paso_fallido, log). Si ok es
    True, paso_fallido es None.
    """
    env = os.environ.copy()
    env["PYTHONPATH"] = ROOT
    env["SSD_ANIO_INICIO"] = str(anio_inicio)
    env["SSD_ANIO_FIN"] = str(anio_fin)
    env["SSD_N_ESTUDIANTES_COHORTE"] = str(n_estudiantes)
    env["SSD_MAX_MATERIAS_SEMESTRE"] = str(max_materias)

    barra = st.progress(0.0)
    for i, (nombre, script) in enumerate(PIPELINE):
        st.write(f"▶ {nombre} …")
        proc = subprocess.run(
            [sys.executable, script],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            return False, nombre, (proc.stdout or "") + "\n" + (proc.stderr or "")
        barra.progress((i + 1) / len(PIPELINE))
    return True, None, None


def exportar_powerbi():
    """Copia los CSV de hechos y dimensiones a powerbi_export/.

    Devuelve (copiados, faltantes).
    """
    os.makedirs(POWERBI_DIR, exist_ok=True)
    copiados, faltantes = [], []
    for nombre in DIMENSIONES:
        origen = os.path.join(CONFIG_DIR, nombre)
        (copiados if os.path.exists(origen) else faltantes).append(nombre)
        if os.path.exists(origen):
            shutil.copy2(origen, os.path.join(POWERBI_DIR, nombre))
    for nombre in HECHOS:
        origen = os.path.join(EXPORT_DIR, nombre)
        (copiados if os.path.exists(origen) else faltantes).append(nombre)
        if os.path.exists(origen):
            shutil.copy2(origen, os.path.join(POWERBI_DIR, nombre))
    return copiados, faltantes


# ---------------------------------------------------------------------------
# Interfaz
# ---------------------------------------------------------------------------
st.set_page_config(page_title="SSD Curricular — Simulación", page_icon="🎓")
st.title("SSD Curricular — Pipeline de simulación")

st.subheader("1. Parámetros")
st.markdown("**Ventana de simulación**")
col1, col2 = st.columns(2)
with col1:
    anio_inicio = st.number_input(
        "Año de inicio",
        min_value=2000,
        max_value=2100,
        value=2018,
        step=1,
        help="Primer año en que ingresan cohortes (default del modelo: 2018).",
    )
with col2:
    anio_fin = st.number_input(
        "Año de fin",
        min_value=2000,
        max_value=2100,
        value=2026,
        step=1,
        help="Último año de la ventana de simulación (default del modelo: 2026).",
    )

col3, col4 = st.columns(2)
with col3:
    n_estudiantes = st.number_input(
        "Estudiantes por cohorte (semestre)",
        min_value=1,
        max_value=200,
        value=25,
        step=1,
        help="Cada semestre entra un grupo nuevo de este tamaño (default: 25).",
    )
with col4:
    max_materias = st.number_input(
        "Máximo de materias por semestre",
        min_value=1,
        max_value=12,
        value=6,
        step=1,
        help="Carga académica máxima por semestre (default: 6).",
    )

# Validación: el año de inicio no puede ser posterior al de fin.
rango_ok = anio_inicio <= anio_fin
if not rango_ok:
    st.warning("El 'Año de inicio' no puede ser posterior al 'Año de fin'.")

st.subheader("2. Ejecución")
st.info(
    "📂 **Antes de arrancar:** copiá manualmente los archivos de datos simulados a "
    "`ssd_core/config/`. La interfaz no automatiza ese paso (es intencional)."
)
if st.button("Arrancar análisis", type="primary", disabled=not rango_ok):
    with st.spinner("Ejecutando el pipeline completo…"):
        ok, paso, log = correr_pipeline(
            int(anio_inicio),
            int(anio_fin),
            int(n_estudiantes),
            int(max_materias),
        )
    if ok:
        st.session_state["analisis_ok"] = True
        st.success(
            f"✅ Análisis completado: ventana {int(anio_inicio)}–{int(anio_fin)}, "
            f"{int(n_estudiantes)} estudiantes por cohorte, "
            f"máx. {int(max_materias)} materias por semestre. "
            "Resultados generados en la carpeta export/."
        )
    else:
        st.session_state["analisis_ok"] = False
        st.error(f"❌ Falló el paso: {paso}")
        st.code(log or "(sin salida)")

st.subheader("3. Exportar para Power BI")
if st.button("Exportar para Power BI"):
    if not st.session_state.get("analisis_ok"):
        st.warning("Primero corré 'Arrancar análisis' para generar los resultados.")
    else:
        copiados, faltantes = exportar_powerbi()
        st.success(
            f"✅ Exportados {len(copiados)} archivos a powerbi_export/ "
            "(hechos + dimensiones, esquema estrella)."
        )
        if faltantes:
            st.info("No se encontraron (se omitieron): " + ", ".join(faltantes))
