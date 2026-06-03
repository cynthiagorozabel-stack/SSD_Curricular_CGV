# Guía de uso: PYTHONPATH y estructura de paquetes en SSD_CGV_V2

## ¿Qué es PYTHONPATH y para qué sirve?

PYTHONPATH es una variable de entorno que le indica a Python dónde buscar los módulos y paquetes cuando ejecutas scripts o tests. Usar PYTHONPATH correctamente permite:
- Realizar imports absolutos (por ejemplo, `from ssd_core.base.config_loader import ConfigLoader`) desde cualquier subdirectorio.
- Ejecutar tests y scripts desde la raíz del proyecto sin problemas de rutas.
- Mejorar la portabilidad: el proyecto funcionará igual en cualquier máquina o entorno.

## Estructura recomendada

El proyecto está organizado como un paquete raíz (`ssd_core`) con submódulos y subpaquetes. Cada carpeta relevante contiene un archivo `__init__.py` para que Python la reconozca como paquete.

```
SSD_CGV_V2/
│   requirements.txt
│   ...
└───ssd_core/
    │   __init__.py
    ├───base/
    │   └── __init__.py
    ├───engines/
    │   └── __init__.py
    ├───tests/
    │   └── __init__.py
    ...
```

## Cómo ejecutar tests y scripts correctamente

1. **Activa el entorno virtual** (si aplica):
   
   En PowerShell:
   ```
   & venv\Scripts\Activate.ps1
   ```

2. **Ejecuta cualquier test o script con PYTHONPATH**:
   
   Desde la raíz del proyecto:
   ```
   set PYTHONPATH=. && venv\Scripts\python.exe -m unittest ssd_core.tests.test_config_loader
   set PYTHONPATH=. && venv\Scripts\python.exe -m unittest ssd_core.tests.test_engines
   set PYTHONPATH=. && venv\Scripts\python.exe ssd_core/simulation/simular_matriculacion.py
   ```
   (En Linux/Mac, usa `export PYTHONPATH=.` en vez de `set`)

3. **Importa siempre usando la ruta absoluta desde la raíz del paquete**:
   
   Ejemplo en tests:
   ```python
   from ssd_core.base.config_loader import ConfigLoader
   from ssd_core.engines.ra_engine import RAEngine
   ```

4. **¿Por qué puede fallar un test?**
   - Si falta un archivo de datos (ejemplo: `config/ra_competencia.csv`), el test fallará con `FileNotFoundError`.
   - Si el import no es absoluto o falta el `__init__.py`, puede dar `ModuleNotFoundError`.

## Resumen de beneficios
- Portabilidad total: funciona igual en cualquier máquina.
- Imports claros y mantenibles.
- Tests y scripts ejecutables desde la raíz, sin modificar rutas.

---

**Recomendación:** Mantén siempre la estructura de paquetes y usa PYTHONPATH al ejecutar scripts/tests. Si agregas nuevos módulos, recuerda crear el archivo `__init__.py` correspondiente.
