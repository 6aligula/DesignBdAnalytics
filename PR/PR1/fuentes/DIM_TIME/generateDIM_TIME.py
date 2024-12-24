import pandas as pd
from datetime import datetime

# Lista de archivos CSV
csv_files = [
    "fuentes/fhv_tripdata-001/fhv_tripdata_2023-10.csv",
    "fuentes/fhv_tripdata-001/fhv_tripdata_2023-11.csv",
    "fuentes/fhv_tripdata-001/fhv_tripdata_2023-12.csv",
    "fuentes/fhv_tripdata-001/fhv_tripdata_2024-01.csv",
    "fuentes/yellow_tripdata-001/yellow_tripdata_2023-10.csv",
    "fuentes/yellow_tripdata-001/yellow_tripdata_2023-11.csv",
    "fuentes/yellow_tripdata-001/yellow_tripdata_2023-12.csv",
    "fuentes/yellow_tripdata-001/yellow_tripdata_2024-01.csv"
]

# Set para almacenar las fechas y horas únicas
unique_datetimes = set()

# Procesar cada archivo CSV
for file in csv_files:
    print(f"Procesando archivo: {file}")
    try:
        # Leer el archivo con low_memory=False para evitar advertencias
        df = pd.read_csv(file, low_memory=False)
        
        # Identificar tipo de archivo y columnas relevantes
        if "pickup_datetime" in df.columns and "dropOff_datetime" in df.columns:  # fhv_tripdata
            pickup_times = pd.to_datetime(df['pickup_datetime'], errors='coerce').dropna()
            dropoff_times = pd.to_datetime(df['dropOff_datetime'], errors='coerce').dropna()
            unique_datetimes.update(pickup_times.tolist())
            unique_datetimes.update(dropoff_times.tolist())
        elif "tpep_pickup_datetime" in df.columns and "tpep_dropoff_datetime" in df.columns:  # yellow_tripdata
            pickup_times = pd.to_datetime(df['tpep_pickup_datetime'], errors='coerce').dropna()
            dropoff_times = pd.to_datetime(df['tpep_dropoff_datetime'], errors='coerce').dropna()
            unique_datetimes.update(pickup_times.tolist())
            unique_datetimes.update(dropoff_times.tolist())
        else:
            print(f"Archivo {file} no tiene columnas esperadas, ignorando.")
    except Exception as e:
        print(f"Error al procesar el archivo {file}: {e}")

# Identificar valores inválidos o nulos
invalid_datetimes = {dt for dt in unique_datetimes if not pd.notnull(dt)}
if invalid_datetimes:
    print("\nValores descartados (inválidos o nulos):")
    for val in invalid_datetimes:
        print(val)

# Eliminar valores inválidos del conjunto
unique_datetimes = {dt for dt in unique_datetimes if pd.notnull(dt)}

# Ordenar y convertir a DataFrame
sorted_datetimes = sorted(unique_datetimes)
records = []

for dt in sorted_datetimes:
    time_id = int(dt.strftime('%Y%m%d%H%M%S'))
    records.append({
        'timeID': time_id,
        'year': dt.year,
        'month': dt.month,
        'day': dt.day,
        'hour': dt.hour,
        'min': dt.minute,
        'sg': dt.second,
        'date': dt
    })

# Crear DataFrame para la tabla DIM_TIME
dim_time_df = pd.DataFrame(records)

# Guardar en un archivo CSV
dim_time_df.to_csv("dim_time.csv", index=False)
print("\nArchivo dim_time.csv generado con éxito.")
