# Bitácora de Cambios y Actividades - 24 de marzo de 2026

## Cambios en el simulador y generación de datos
- Se modificó el simulador de matriculación para garantizar al menos 20 estudiantes por cada nivel máximo (PRIMER a NOVENO) en todas las cohortes simuladas.
- Se implementó progresión estricta: cada estudiante solo puede alcanzar un nivel si ha aprobado todos los niveles anteriores.
- Se ejecutó el simulador y se verificó la correcta generación de los archivos de datos.

## Análisis de exportaciones SSD
- Se revisaron los archivos exportados (ra_logro_individual.csv, competencia_logro_individual.csv, perfil_logro_individual.csv, ra_logro_matrix.csv).
- Se confirmó que los archivos reflejan la progresión académica real y cumplen la función de un SSD: seguimiento longitudinal, cálculo de logros por RA, competencia y perfil, y trazabilidad de avance.
- Se verificó que hay estudiantes con nivel máximo en todos los niveles y que la progresión es coherente.

## Explicaciones y hallazgos
- Se explicó por qué los estudiantes de primer nivel tienen un perfil promedio elevado: solo cursan materias iniciales, con notas aleatorias y sin materias avanzadas que bajen el promedio.
- Se describió el archivo ra_logro_matrix.csv como una matriz de logros por RA y competencias, útil para análisis y visualización del avance académico.

## Conclusión
El sistema y el simulador cumplen con los requisitos de un SSD, generando datos consistentes y útiles para el seguimiento y análisis académico.
