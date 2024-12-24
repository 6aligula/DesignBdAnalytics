import csv

# Ruta del archivo original y del archivo CSV de salida
input_file = 'Rate_code.tab'
output_file = 'Rate_code.csv'

# Leer el archivo .tab y escribirlo como un archivo .csv
with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
    reader = (line.strip().split('\t') for line in infile)  # Leer y dividir por tabulaciones
    writer = csv.writer(outfile)
    
    # Escribir encabezados
    writer.writerow(['RateID', 'RateName'])
    
    # Escribir datos
    writer.writerows(reader)

print(f"Archivo CSV generado en: {output_file}")
