import pandas as pd

file_path = './yellow_tripdata-001/yellow_tripdata_2023-12.csv'

# Cargar datos sin procesar valores nulos ni espacios
data = pd.read_csv(file_path, keep_default_na=False, skipinitialspace=False)

# Identificar valores inesperados (excluyendo N, Y y valores nulos explícitos)
unexpected_values = data[
    ~data['store_and_fwd_flag'].isin(['N', 'Y', ''])  # Excluir valores válidos y vacíos
]['store_and_fwd_flag'].dropna().unique()

print("Valores inesperados encontrados:")
print(unexpected_values)
