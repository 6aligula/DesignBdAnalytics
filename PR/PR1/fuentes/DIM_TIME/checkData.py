import pandas as pd

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

# Función para analizar fechas y horas
def analyze_datetime_columns(df, file_name, datetime_columns):
    for col in datetime_columns:
        if col in df.columns:
            print(f"\nAnálisis de la columna '{col}' en el archivo '{file_name}':")
            
            # Convertir a datetime y contar valores nulos
            converted = pd.to_datetime(df[col], errors='coerce')
            null_count = converted.isnull().sum()
            total_count = len(df[col])
            
            print(f"  - Total de valores: {total_count}")
            print(f"  - Valores nulos o inválidos: {null_count}")
            
            # Tipos de valores originales (antes de conversión)
            print(f"  - Tipos originales:")
            print(df[col].apply(type).value_counts())
            
            # Valores más comunes (para detectar patrones anómalos)
            print(f"  - Valores más comunes:")
            print(df[col].value_counts(dropna=False).head(5))

# Procesar cada archivo
for file in csv_files:
    print(f"\n--- Analizando archivo: {file} ---")
    try:
        df = pd.read_csv(file, low_memory=False)
        
        # Columnas posibles que contienen fechas y horas
        datetime_columns = [
            "pickup_datetime", 
            "dropOff_datetime", 
            "tpep_pickup_datetime", 
            "tpep_dropoff_datetime"
        ]
        
        # Analizar columnas relacionadas con fechas y horas
        analyze_datetime_columns(df, file, datetime_columns)
    except Exception as e:
        print(f"Error al procesar el archivo {file}: {e}")
