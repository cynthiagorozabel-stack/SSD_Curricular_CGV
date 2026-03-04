import pandas as pd
import sys

if len(sys.argv) < 2:
    print("Uso: python check_column_types.py <ruta_csv>")
    sys.exit(1)

csv_path = sys.argv[1]
df = pd.read_csv(csv_path)

print(f"Analizando tipos de columnas en: {csv_path}\n")
for col in df.columns:
    dtype = str(df[col].dtype)
    unique_types = set(type(x).__name__ for x in df[col].dropna())
    print(f"Columna: {col:30} | dtype: {dtype:10} | Tipos únicos: {unique_types}")
    if dtype == 'object' or any(t not in ['int64', 'float64'] for t in unique_types):
        print(f"  -> ¡Atención! Esta columna contiene valores no numéricos.")
