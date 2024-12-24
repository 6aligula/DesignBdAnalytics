import pandas as pd

# Leer el archivo TSV
df = pd.read_csv('CURRENT_BASES.tsv', sep='\t')

# Guardar como CSV
df.to_csv('CURRENT_BASES.csv', index=False)
