import pandas as pd

# Ruta al archivo
file_path = './yellow_tripdata-001/yellow_tripdata_2023-12.csv'

# Cargar el archivo
data = pd.read_csv(file_path, keep_default_na=False)

# Comprobar si existe la columna `store_and_fwd_flag`
if 'store_and_fwd_flag' in data.columns:
    # Listar valores únicos
    unique_values = data['store_and_fwd_flag'].unique()
    
    # Filtrar valores diferentes de 'N', 'Y' o nulos
    unexpected_values = data[~data['store_and_fwd_flag'].isin(['N', 'Y'])]['store_and_fwd_flag'].dropna().unique()
    
    # Contar frecuencias de todos los valores
    value_counts = data['store_and_fwd_flag'].value_counts(dropna=False)
    
    print("Valores únicos encontrados:")
    print(unique_values)
    print("\nFrecuencia de cada valor:")
    print(value_counts)
    
    print("\nValores inesperados encontrados:")
    print(unexpected_values)
else:
    print("La columna 'store_and_fwd_flag' no existe en el archivo.")
