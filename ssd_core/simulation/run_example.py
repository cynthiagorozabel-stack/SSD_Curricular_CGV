# run_example.py
# Generador de datos simulados para pruebas del SSD Curricular
import pandas as pd
import numpy as np
import os
import sys
from simular_matriculacion import *

class SimulationEngine:
    def __init__(self, n_estudiantes=10):
        self.n_estudiantes = n_estudiantes

    def generate(self):
        # Genera datos simulados de RA, competencias y riesgos
        estudiantes = [f"E{i+1}" for i in range(self.n_estudiantes)]
        ra = pd.DataFrame({
            'ID_EST': estudiantes,
            'RA1': np.random.uniform(0.5, 1.0, self.n_estudiantes),
            'RA2': np.random.uniform(0.5, 1.0, self.n_estudiantes),
            'RA3': np.random.uniform(0.5, 1.0, self.n_estudiantes)
        })
        riesgos = pd.DataFrame({
            'ID_EST': estudiantes,
            'desempeño': np.random.uniform(0.6, 1.0, self.n_estudiantes),
            'repitencia': np.random.randint(0, 2, self.n_estudiantes),
            'deserción': np.random.randint(0, 2, self.n_estudiantes)
        })
        return ra, riesgos

def main():
    sim = SimulationEngine(n_estudiantes=10)
    ra, riesgos = sim.generate()
    print("Datos simulados RA:")
    print(ra.head())
    print("Datos simulados riesgos:")
    print(riesgos.head())

    # Ejecuta la simulación de matriculación histórica
    print("Simulando matriculación histórica...")
    # simular_matriculacion.py ya genera el archivo CSV
    # Si quieres ver los primeros registros:
    import csv
    path = '../config/matriculacion_historica_test.csv' if not os.path.exists('ssd_core/config/matriculacion_historica_test.csv') else 'ssd_core/config/matriculacion_historica_test.csv'
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            print(row)
            if i > 10:
                break
    print("Simulación completada.")

if __name__ == "__main__":
    main()