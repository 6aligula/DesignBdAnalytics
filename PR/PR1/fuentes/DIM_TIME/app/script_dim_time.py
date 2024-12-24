# app/script_dim_time.py

import os
import pandas as pd
import pyodbc
from datetime import datetime
from tqdm import tqdm
import time
import traceback

print("Iniciando script_dim_time.py")

# Configuración de la conexión a la base de datos usando variables de entorno
SQL_SERVER = os.getenv('SQL_SERVER', 'localhost')
SQL_DATABASE = os.getenv('SQL_DATABASE', 'DIM_TIME_DB')  # Reemplaza con el nombre real de tu base de datos
SQL_USER = os.getenv('SQL_USER', 'sa')
SQL_PASSWORD = os.getenv('SQL_PASSWORD', 'YourStrongPassword!123')

print(f"Configuración de conexión: Servidor={SQL_SERVER}, Base de datos={SQL_DATABASE}, Usuario={SQL_USER}")

# Conexión a la base de datos 'master' para gestionar la creación de la base de datos
master_conn_str = (
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={SQL_SERVER};'
    f'DATABASE=master;'
    f'UID={SQL_USER};'
    f'PWD={SQL_PASSWORD}'
)

# Función para esperar hasta que SQL Server esté listo
def wait_for_sql_server(conn_str, timeout=120):
    start_time = time.time()
    while True:
        try:
            print("Intentando conectar con SQL Server...")
            conn = pyodbc.connect(conn_str, timeout=5)
            conn.close()
            print("Conexión a SQL Server establecida.")
            break
        except pyodbc.Error as e:
            if time.time() - start_time > timeout:
                print("Timeout al intentar conectar con SQL Server.")
                traceback.print_exc()
                raise TimeoutError("Timeout al intentar conectar con SQL Server.")
            print("Esperando a que SQL Server esté listo...")
            time.sleep(5)

# Esperar a que SQL Server esté listo
wait_for_sql_server(master_conn_str)

# Función para crear la base de datos si no existe
def create_database_if_not_exists():
    try:
        print(f"Verificando si la base de datos '{SQL_DATABASE}' existe...")
        conn = pyodbc.connect(master_conn_str)
        cursor = conn.cursor()
        cursor.execute(f"""
        IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'{SQL_DATABASE}')
        BEGIN
            CREATE DATABASE [{SQL_DATABASE}];
            PRINT 'Base de datos {SQL_DATABASE} creada.';
        END
        ELSE
        BEGIN
            PRINT 'La base de datos {SQL_DATABASE} ya existe.';
        END
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Base de datos '{SQL_DATABASE}' verificada/creada.")
    except Exception as e:
        print(f"Error al crear/verificar la base de datos: {e}")
        traceback.print_exc()

# Función para crear la tabla DIM_TIME si no existe
def create_table_if_not_exists():
    try:
        conn_str = (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={SQL_SERVER};'
            f'DATABASE={SQL_DATABASE};'
            f'UID={SQL_USER};'
            f'PWD={SQL_PASSWORD}'
        )
        print(f"Conectando a la base de datos '{SQL_DATABASE}' para verificar/crear la tabla 'DIM_TIME'...")
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[DIM_TIME]') AND type in (N'U'))
        BEGIN
            CREATE TABLE [dbo].[DIM_TIME](
                [timeID] [numeric](18, 0) NOT NULL,
                 NULL,
                 NULL,
                 NULL,
                 NULL,
                 NULL,
                 NULL,
                [date] [datetime] NOT NULL,
             CONSTRAINT [PK_DIM_TIME] PRIMARY KEY CLUSTERED 
            (
                [timeID] ASC
            )
            ) ON [PRIMARY];
            PRINT 'Tabla DIM_TIME creada.';
        END
        ELSE
        BEGIN
            PRINT 'La tabla DIM_TIME ya existe.';
        END
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("Tabla 'DIM_TIME' verificada/creada.")
    except Exception as e:
        print(f"Error al crear/verificar la tabla 'DIM_TIME': {e}")
        traceback.print_exc()

# Crear la base de datos y la tabla si no existen
create_database_if_not_exists()
create_table_if_not_exists()

# Establecer la conexión a la base de datos específica
conn_str = (
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={SQL_SERVER};'
    f'DATABASE={SQL_DATABASE};'
    f'UID={SQL_USER};'
    f'PWD={SQL_PASSWORD}'
)

try:
    print("Estableciendo conexión con la base de datos específica...")
    conn = pyodbc.connect(conn_str)
    print("Conexión establecida.")
    cursor = conn.cursor()
    print("Cursor creado.")
except Exception as e:
    print(f"Error al conectar con la base de datos específica: {e}")
    traceback.print_exc()
    exit(1)

# Directorio donde se encuentran los archivos CSV
base_dir = 'fuentes'

# Listado de carpetas y archivos
folders = [
    'fhv_tripdata-001',
    'yellow_tripdata-001'
]

# Función para generar timeID basado en datetime
def generate_time_id(dt):
    return int(dt.strftime('%Y%m%d%H%M%S'))

# Función para extraer datetime de filas de diferentes formatos
def extract_datetimes(df, trip_type):
    datetimes = set()
    if trip_type == 'yellow':
        pickup = pd.to_datetime(df['tpep_pickup_datetime'], errors='coerce')
        dropoff = pd.to_datetime(df['tpep_dropoff_datetime'], errors='coerce')
    elif trip_type == 'fhv':
        pickup = pd.to_datetime(df['pickup_datetime'], errors='coerce')
        dropoff = pd.to_datetime(df['dropOff_datetime'], errors='coerce')
    else:
        pickup = dropoff = pd.NaT

    datetimes.update(pickup.dropna().tolist())
    datetimes.update(dropoff.dropna().tolist())
    return datetimes

# Paso 1: Extraer todas las fechas y horas únicas de los archivos CSV
print("Paso 1: Extrayendo fechas y horas únicas de los archivos CSV...")
all_datetimes = set()

for folder in folders:
    trip_type = 'yellow' if 'yellow' in folder else 'fhv'
    folder_path = os.path.join(base_dir, folder)
    print(f"Procesando carpeta: {folder_path}")
    for file in os.listdir(folder_path):
        if file.endswith('.csv'):
            file_path = os.path.join(folder_path, file)
            print(f"Leyendo {file_path}...")
            try:
                # Leer en chunks para manejar grandes archivos
                for chunk in pd.read_csv(file_path, chunksize=100000):
                    datetimes = extract_datetimes(chunk, trip_type)
                    all_datetimes.update(datetimes)
                print(f"Procesado {file_path} correctamente.")
            except Exception as e:
                print(f"Error leyendo {file_path}: {e}")
                traceback.print_exc()

print(f"Total de fechas y horas extraídas: {len(all_datetimes)}")

# Paso 2: Obtener las fechas y horas ya existentes en DIM_TIME
print("Paso 2: Obteniendo fechas y horas existentes en DIM_TIME...")
try:
    cursor.execute("SELECT [date] FROM dbo.DIM_TIME")
    existing_dates = set(row[0] for row in cursor.fetchall())
    print(f"Fechas y horas ya existentes en DIM_TIME: {len(existing_dates)}")
except Exception as e:
    print(f"Error obteniendo fechas existentes: {e}")
    traceback.print_exc()
    existing_dates = set()

# Paso 3: Determinar las nuevas fechas y horas a insertar
print("Paso 3: Determinando nuevas fechas y horas a insertar...")
new_datetimes = all_datetimes - existing_dates
print(f"Nuevas fechas y horas a insertar: {len(new_datetimes)}")

# Si no hay nuevas fechas, terminar el proceso
if not new_datetimes:
    print("No hay nuevas fechas y horas para insertar.")
    conn.close()
    print("Conexión cerrada.")
    exit(0)

# Paso 4: Preparar los nuevos registros para insertar
print("Paso 4: Preparando nuevos registros para insertar...")
records_to_insert = []
for dt in new_datetimes:
    try:
        year = dt.strftime('%Y')
        month = dt.strftime('%m')
        day = dt.strftime('%d')
        hour = dt.strftime('%H')
        minute = dt.strftime('%M')
        second = dt.strftime('%S')
        date = dt
        time_id = generate_time_id(dt)
        records_to_insert.append((time_id, year, month, day, hour, minute, second, date))
    except Exception as e:
        print(f"Error procesando datetime {dt}: {e}")
        traceback.print_exc()

print(f"Total de registros a insertar: {len(records_to_insert)}")

# Paso 5: Insertar los nuevos registros en DIM_TIME en lotes
print("Paso 5: Insertando nuevos registros en DIM_TIME...")
batch_size = 10000
for i in tqdm(range(0, len(records_to_insert), batch_size)):
    batch = records_to_insert[i:i + batch_size]
    try:
        # Preparar el comando de inserción
        values_str = ",".join(["(?, ?, ?, ?, ?, ?, ?, ?)"] * len(batch))
        sql = f"""
        INSERT INTO dbo.DIM_TIME (timeID, [year], [month], [day], [hour], [min], [sg], [date])
        VALUES {values_str}
        """
        # Aplanar la lista de tuplas para pasar como parámetros
        params = [item for record in batch for item in record]
        cursor.execute(sql, params)
        conn.commit()
        print(f"Lote {i // batch_size + 1} insertado correctamente.")
    except Exception as e:
        print(f"Error insertando el lote {i // batch_size + 1}: {e}")
        traceback.print_exc()
        conn.rollback()

print("Inserción completada.")

# Cerrar la conexión
conn.close()
print("Conexión cerrada.")
