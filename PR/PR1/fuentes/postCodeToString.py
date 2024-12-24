import pandas as pd

# Cargar el archivo CSV
file_path = "CURRENT_BASES_UPDATED.csv"  # Ruta al archivo actual
output_path = "CURRENT_BASES_UPDATED_PostCode.csv"  # Ruta al archivo actualizado

# Leer el archivo CSV
data = pd.read_csv(file_path)

# Convertir la columna Postcode a string
data["Postcode"] = data["Postcode"].astype(str)

# Guardar el archivo actualizado
data.to_csv(output_path, index=False)

print(f"Archivo actualizado guardado en {output_path}")
