import pandas as pd
import os

def analyze_vendorid(file_path):
    """
    Analyze the 'VendorID' column in a CSV file.

    Parameters:
        file_path (str): Path to the CSV file.

    Returns:
        dict: Summary of the 'VendorID' column analysis.
    """
    try:
        # Load the CSV file with low_memory=False to prevent DtypeWarning
        data = pd.read_csv(file_path, low_memory=False)

        # Check if 'VendorID' column exists
        if 'VendorID' not in data.columns:
            return {
                "error": "Column 'VendorID' not found in the dataset.",
                "file": file_path
            }

        # Analyze the 'VendorID' column
        result = {
            "file": file_path,
            "null_values": data['VendorID'].isnull().sum(),
            "empty_strings": (data['VendorID'] == "").sum(),
            "unique_values": data['VendorID'].unique().tolist(),
            "head": data['VendorID'].head().tolist()
        }
        return result

    except Exception as e:
        return {
            "error": str(e),
            "file": file_path
        }


# Example usage:

# Carpeta donde están los archivos CSV
folder_path = "yellow_tripdata-001"

# Lista de archivos CSV en la carpeta
files = [
    os.path.join(folder_path, "yellow_tripdata_2023-10.csv"),
    os.path.join(folder_path, "yellow_tripdata_2023-11.csv"),
    os.path.join(folder_path, "yellow_tripdata_2023-12.csv"),
    os.path.join(folder_path, "yellow_tripdata_2024-01.csv")
]

# Analizar cada archivo
for file in files:
    result = analyze_vendorid(file)
    print(result)

