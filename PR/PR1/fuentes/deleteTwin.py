import pandas as pd

# Cargar el archivo CSV
file_path = "CURRENT_BASES.csv"  # Ruta del archivo
data = pd.read_csv(file_path)

# Contar el número de registros antes de la eliminación
initial_count = data.shape[0]

# Eliminar duplicados del número de licencia B02920, manteniendo solo la primera aparición
data = data[~((data["License Number"] == "B02920") & (data.duplicated(subset=["License Number"], keep="first")))]

# Contar el número de registros después de la eliminación
final_count = data.shape[0]

# Mostrar los resultados
print(f"Registros antes de la eliminación: {initial_count}")
print(f"Registros después de la eliminación: {final_count}")

# Guardar el archivo actualizado
data.to_csv("CURRENT_BASES_UPDATED.csv", index=False)