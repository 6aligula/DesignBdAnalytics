import pandas as pd

# Ruta del archivo CSV
input_file = "CURRENT_BASES_UPDATED_PostCode.csv"  # Archivo original
output_file = "CURRENT_BASES_UPDATED_PostCode_Spaces.csv"  # Archivo con encabezados modificados

# Diccionario para mapear los nombres de las columnas
column_mapping = {
    "License Number": "[LicenseNumber] VARCHAR(6) PRIMARY KEY",
    "Entity Name": "[EntityName] VARCHAR(60) NULL",
    "Telephone Number": "[TelephoneNumber] INT NULL",
    "SHL Endorsed": "[SHLEndorsed] VARCHAR(3) NULL",
    "Building": "[Building] VARCHAR(15) NULL",
    "Street": "[Street] VARCHAR(50) NULL",
    "City": "[City] VARCHAR(15) NULL",
    "State": "[State] CHAR(2) NULL",
    "Postcode": "[Postcode] VARCHAR(15) NULL",
    "Type of Base": "[TypeOfBase] VARCHAR(27) NULL",
    "Latitude": "[Latitude] FLOAT NULL",
    "Longitude": "[Longitude] FLOAT NULL",
    "Date": "[Date] DATE NULL",
    "Time": "[Time] VARCHAR(8) NULL",
    "Location": "[Location] VARCHAR(25) NULL"
}

# Leer el archivo CSV
data = pd.read_csv(input_file)

# Renombrar las columnas usando el mapeo
data.columns = [column_mapping[col] for col in data.columns]

# Guardar el archivo con los nuevos encabezados
data.to_csv(output_file, index=False)

print(f"Encabezados modificados y archivo guardado como {output_file}")
