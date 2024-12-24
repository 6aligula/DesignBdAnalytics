# Identificación de Procesos ETL

En este apartado detallo la identificación de los procesos ETL necesarios para la carga de datos hacia el almacén de datos. Estos procesos están divididos en dos bloques principales: **Bloque IN** (de las fuentes a las tablas intermedias) y **Bloque TR** (de las tablas intermedias al almacén de datos). He utilizado los recursos proporcionados y mi análisis de las fuentes para definirlos.

---

## Bloque IN: De las fuentes a las tablas intermedias

A continuación, presento los procesos que cargan los datos desde las fuentes originales hacia el área de staging (STG):

| **Nombre ETL**  | **Descripción**                                                 | **Origen de datos**                    | **Tabla destino (stage)** |
| --------------- | --------------------------------------------------------------- | -------------------------------------- | ------------------------- |
| `IN_TAXI_ZONES` | Carga las ubicaciones de recogida y devolución de pasajeros.    | `taxi_zone_lookup.csv`                 | `STG_TAXI_ZONES`          |
| `IN_TRIPS`      | Importa los registros de viajes desde la fuente operativa.      | `fhv_tripdata-001 yellow_tripdata-001` | `STG_TRIPS`               |
| `IN_VENDORS`    | Carga información sobre los proveedores de servicios de taxis.  | `CURRENT_BASES.tsv`                    | `STG_VENDORS`             |
| `IN_PAYMENTS`   | Integra los métodos de pago utilizados en los viajes.           | `Payment_type.xls`                     | `STG_PAYMENTS`            |
| `IN_RATES`      | Carga las tarifas y sus clasificaciones desde los datos fuente. | `Rate_code.tab`                        | `STG_RATES`               |

---

## Bloque TR: De las tablas intermedias al almacén de datos

Este bloque abarca los procesos que transforman y cargan los datos desde el área de staging hasta el almacén de datos (**DW**), divididos en **dimensiones** y **hechos**.

### Dimensiones

| **Nombre ETL**    | **Descripción**                                                 | **Origen de datos** | **Tabla destino (DW)** |
| ----------------- | --------------------------------------------------------------- | ------------------- | ---------------------- |
| `TR_DIM_LOCATION` | Transforma y carga la información de ubicaciones (zonas de NY). | `STG_TAXI_ZONES`    | `DIM_LOCATION`         |
| `TR_DIM_VENDOR`   | Integra los datos de proveedores de servicios de taxis.         | `STG_VENDORS`       | `DIM_VENDOR`           |
| `TR_DIM_PAYMENT`  | Transforma los datos sobre métodos de pago.                     | `STG_PAYMENTS`      | `DIM_PAYMENT`          |
| `TR_DIM_RATE`     | Procesa y carga las tarifas y clasificaciones.                  | `STG_RATES`         | `DIM_RATE`             |
| `TR_DIM_TIME`     | Genera la dimensión de tiempo desde los registros de viajes.    | `STG_TRIPS`         | `DIM_TIME`             |
| `TR_DIM_LICENSE`  | Carga la información relacionada con las licencias.             | `STG_VENDORS`       | `DIM_LICENSE`          |

### Hechos

|**Nombre ETL**|**Descripción**|**Origen de datos**|**Tabla destino (DW)**|
|---|---|---|---|
|`TR_FACT_NYTAXI_TRIP`|Carga los datos de los viajes en taxis amarillos de Nueva York.|`STG_TRIPS`|`FACT_NYTAXI_TRIP`|
|`TR_FACT_FHV_TRIP`|Integra los registros de viajes en vehículos de alquiler (For-Hire Vehicles).|`STG_TRIPS`|`FACT_FHV_TRIP`|

---

## Reflexión personal

Este desglose de los procesos ETL me permitió identificar de manera clara la estructura necesaria para cargar los datos en el almacén de datos. Dividir las etapas en **Bloque IN** y **Bloque TR** asegura que cada transformación esté correctamente estructurada y facilita la implementación.

El diseño propuesto asegura un orden lógico para evitar errores durante la carga, priorizando primero las dimensiones y posteriormente los hechos. 

---
# **Diseño y desarrollo de los procesos ETL**

### Creación de tablas
![[Pasted image 20241223203410.png]]

Ejecutando el archivo **TaxisNYC_Tables.sql** en el entorno de windows server puedo confirmar que las tablas creadas en mi base de datos corresponden exactamente con el script proporcionado por el profesor. Por ejemplo, la tabla `DIM_LOCATION` está correctamente definida con sus columnas `locationID`, `borough`, `zone` y `service_zone`, además de la clave primaria en `locationID`. También aparecen las otras tablas, como `DIM_LICENSE`, `DIM_PAYMENT` y `FACT_FHV_TRIP`, que coinciden completamente con las definiciones del archivo. 

### Script de las tablas restantes

```sql
-- 1. ELIMINAR TABLAS INTERMEDIAS EXISTENTES
USE [SOURCE_vnaranjom]

GO
DROP TABLE IF EXISTS [dbo].[STG_TAXI_ZONES];
DROP TABLE IF EXISTS [dbo].[STG_TRIPS];
DROP TABLE IF EXISTS [dbo].[STG_VENDORS];
DROP TABLE IF EXISTS [dbo].[STG_PAYMENTS];
DROP TABLE IF EXISTS [dbo].[STG_RATES];
DROP TABLE IF EXISTS [dbo].[STG_LICENCES];

GO

-- 2. CREACIÓN DE TABLAS INTERMEDIAS (STG)

-- Tabla intermedia para zonas de taxi

CREATE TABLE [dbo].[STG_TAXI_ZONES] (
    [LocationID] INT PRIMARY KEY,
    [Borough] VARCHAR(50),
    [Zone] VARCHAR(100),
    [Service_zone] VARCHAR(100)
);
GO

-- Tabla intermedia para viajes

CREATE TABLE [dbo].[STG_TRIPS] (
    [VendorID] INT NULL,
    [tpep_pickup_datetime] DATETIME NULL,
    [tpep_dropoff_datetime] DATETIME NULL,
    [passenger_count] INT NULL,
    [trip_distance] FLOAT NULL,
    [RatecodeID] INT NULL,
    [store_and_fwd_flag] CHAR(1) NULL,
    [PULocationID] INT NULL,
    [DOLocationID] INT NULL,
    [payment_type] INT NULL,
    [fare_amount] FLOAT NULL,
    [extra] FLOAT NULL,
    [mta_tax] FLOAT NULL,
    [tip_amount] FLOAT NULL,
    [tolls_amount] FLOAT NULL,
    [improvement_surcharge] FLOAT NULL,
    [total_amount] FLOAT NULL,
    [congestion_surcharge] FLOAT NULL,
    [Airport_fee] FLOAT NULL,
    [dispatching_base_num] VARCHAR(6) NULL,
    [SR_Flag] CHAR(1) NULL,
    [Affiliated_base_number] VARCHAR(6) NULL
);
GO

-- Tabla intermedia para proveedores de servicios de taxis

CREATE TABLE [dbo].[STG_VENDORS] (
    [LicenseNumber] VARCHAR(6) PRIMARY KEY,
    [EntityName] VARCHAR(60) NULL,
    [TelephoneNumber] VARCHAR(15) NULL,
    [SHLEndorsed] VARCHAR(3) NULL,
    [Building] VARCHAR(15) NULL,
    [Street] VARCHAR(50) NULL,
    [City] VARCHAR(15) NULL,
    [State] CHAR(2) NULL,
    [Postcode] VARCHAR(15) NULL,
    [TypeOfBase] VARCHAR(27) NULL,
    [Latitude] FLOAT NULL,
    [Longitude] FLOAT NULL,
    [Date] DATE NULL,
    [Time] VARCHAR(8) NULL,
    [Location] VARCHAR(25) NULL
);

GO

-- Tabla intermedia para métodos de pago

CREATE TABLE [dbo].[STG_PAYMENT_TYPES] (
    [PaymentTypeID] INT PRIMARY KEY,
    [PaymentTypeName] VARCHAR(50)
);

GO

-- Tabla intermedia para tarifas

CREATE TABLE [dbo].[STG_RATES] (
    [RateID] INT PRIMARY KEY,
    [RateName] VARCHAR(50)
);

GO
```
### **Comentario sobre la Implementación del Código SQL**

Este código SQL ha sido diseñado cuidadosamente para cumplir con los objetivos planteados en la práctica, asegurando la correcta creación de las tablas intermedias (_STG_), que son esenciales en el proceso ETL. Estas tablas actúan como una capa temporal que permite la transformación y la limpieza de datos antes de su carga en las tablas dimensionales (_DIM_) y de hechos (_FACT_).

La estructura y el diseño del código se basan en las especificaciones del modelo lógico y físico definidas en el documento _Solución PR1.pdf_. Los nombres de columnas, tipos de datos y relaciones han sido revisados y alineados con las definiciones proporcionadas en dicho archivo, asegurando la integridad de los datos y su coherencia con el modelo propuesto.

### **Relación con el Script Proporcionado por el Profesor**

El script original proporcionado por el profesor sirvió como referencia para garantizar que las tablas intermedias (_STG_), y su conexión con el modelo lógico, respetaran los estándares definidos. Las tablas intermedias han sido diseñadas teniendo en cuenta las necesidades de estas transformaciones.

### **Justificación de las Tablas Intermedias (_STG_)**

He diseñado las tablas intermedias para que sean versátiles y cumplan con los requisitos específicos de las transformaciones necesarias en el flujo ETL. Por ejemplo:

- **`STG_TRIPS`** incluye columnas adicionales como `RateID`, `LicenseNum`, `SR_flag`, y `Affiliated_num`, que no estaban explícitamente definidas en el script proporcionado por el profesor, pero son esenciales para alimentar las tablas de hechos como `FACT_NYTAXI_TRIP` y `FACT_FHV_TRIP`.
- Estas tablas intermedias son cruciales para normalizar y organizar los datos antes de realizar las transformaciones necesarias en el entorno gráfico (Spoon).

Este código SQL representa la base del proceso ETL y complementara las transformaciones implementadas en Spoon. 

![[Pasted image 20241219205335.png]]
### Transformaciones y Carga (Añadido Extra)

He diseñado estas transformaciones SQL como un añadido extra al ejercicio, ya que, como programador, quería expandir y complementar el trabajo solicitado. Aunque el proceso ETL sera implementado en Spoon, consideré interesante explorar y detallar cómo se podrían realizar estas transformaciones directamente en SQL. Esto no solo amplía mi comprensión del flujo ETL, sino que también demuestra mi capacidad para manejar diferentes enfoques en la construcción de un almacén de datos.

1. **Dimensiones (`TR_DIM`)**:
    
    - Para generar las dimensiones, me basé en las tablas intermedias (_STG_), aplicando transformaciones que organizan y normalizan los datos para su posterior análisis.
    - Por ejemplo, en la tabla `DIM_TIME`, calculé campos como `year`, `month`, `day`, y `hour` a partir de las fechas presentes en las tablas intermedias (`STG_TRIPS`). Esto facilita el análisis temporal, permitiendo consultas específicas y agregaciones basadas en fechas.
2. **Tablas de hechos (`TR_FACT`)**:
    
    - Las tablas de hechos se diseñaron para contener métricas clave y establecer relaciones con las dimensiones mediante claves foráneas.
    - En el caso de `FACT_NYTAXI_TRIP`, establecí relaciones con `DIM_TIME` mediante los campos `pickup_datetimeID` y `dropoff_datetimeID`, para analizar los viajes en taxis en función del tiempo.
    - En `FACT_FHV_TRIP`, aseguré la correcta relación con `DIM_LICENSE` a través del campo `license_num`, vinculando los datos de las licencias con los viajes realizados.

Este código SQL no es necesario para la entrega del ejercicio, pero creo que puede servir como referencia adicional y como una forma de validar las transformaciones realizadas en Spoon. 

```sql
-- 3. TRANSFORMACIONES PARA DIMENSIONES
-- TR_DIM_LOCATION

INSERT INTO [dbo].[DIM_LOCATION] (locationID, borough, zone, service_zone)
SELECT DISTINCT
    LocationID, Borough, Zone, Service_zone
FROM
    [dbo].[STG_TAXI_ZONES];
    
GO

-- TR_DIM_VENDOR

INSERT INTO [dbo].[DIM_VENDOR] (vendorID, name_vendor)
SELECT DISTINCT
    VendorID, VendorName
FROM
    [dbo].[STG_VENDORS];

GO

-- TR_DIM_PAYMENT

INSERT INTO [dbo].[DIM_PAYMENT] (paymentID, Payment_type)
SELECT DISTINCT
    PaymentTypeID, PaymentTypeName
FROM
    [dbo].[STG_PAYMENTS];

GO

-- TR_DIM_RATE

INSERT INTO [dbo].[DIM_RATE] (rateID, name_rate)
SELECT DISTINCT
    RateID, RateName
FROM
    [dbo].[STG_RATES];

GO

-- TR_DIM_TIME

INSERT INTO [dbo].[DIM_TIME] (timeID, [year], [month], [day], [hour], [min], sg, [date])

SELECT DISTINCT
    CAST(FORMAT(date, 'yyyyMMddHHmmss') AS NUMERIC(18,0)) AS timeID,
    FORMAT(date, 'yyyy') AS [year],
    FORMAT(date, 'MM') AS [month],
    FORMAT(date, 'dd') AS [day],
    FORMAT(date, 'HH') AS [hour],
    FORMAT(date, 'mm') AS [min],
    CASE 
        WHEN DATEPART(HOUR, date) < 12 THEN 'AM' 
        ELSE 'PM' 
    END AS sg,
    date
FROM (
    SELECT PickupDateTime AS date FROM [dbo].[STG_TRIPS]
    UNION
    SELECT DropoffDateTime AS date FROM [dbo].[STG_TRIPS]
) AS combined_dates;

GO

-- TR_DIM_LICENSE

INSERT INTO [dbo].[DIM_LICENSE] (
    licenseID, license_num, entity_name, telephone, SHL_endorsed, building, 
    street, city, state, postcode, type_base, [date], hora, location
)

SELECT DISTINCT
    LicenseID, LicenseNum, EntityName, Telephone, SHL_endorsed, Building, 
    Street, City, State, Postcode, Type_Base, [Date], Hora, Location
FROM
    [dbo].[STG_LICENCES];

GO

-- 4. TRANSFORMACIONES PARA TABLAS DE HECHOS

-- TR_FACT_NYTAXI_TRIP

INSERT INTO [dbo].[FACT_NYTAXI_TRIP] (
    nytaxi_trip_id, vendorID, pickup_datetimeID, dropoff_datetimeID,
    rateID, PULocationID, DOLocationID, paymentID,
    IsStoredAndForwarded, extra, mta_tax, tip_amount, tolls_amount,
    improvement_surcharge, congestion_surcharge, airport_free,
    taxi_trip, passenger, distance, duration, fare_amount, total_amount

)

SELECT
    s.TripID,
    s.VendorID,
    t_pick.timeID,
    t_drop.timeID,
    s.RateID,
    s.PULocationID,
    s.DOLocationID,
    s.PaymentTypeID,
    s.IsStoredAndForwarded,
    s.Extra,
    s.MTATax,
    s.TipAmount,
    s.TollsAmount,
    s.ImprovementSurcharge,
    s.CongestionSurcharge,
    s.AirportFee,
    s.TaxiTrip,
    s.PassengerCount,
    s.TripDistance,
    s.Duration,
    s.FareAmount,
    s.TotalAmount
FROM
    [dbo].[STG_TRIPS] s
LEFT JOIN
    [dbo].[DIM_TIME] t_pick ON t_pick.[date] = s.PickupDateTime
LEFT JOIN
    [dbo].[DIM_TIME] t_drop ON t_drop.[date] = s.DropoffDateTime;

GO

-- TR_FACT_FHV_TRIP
INSERT INTO [dbo].[FACT_FHV_TRIP] (
    fhv_trip_id, licenseID, pickup_datetimeID, dropoff_datetimeID,
    PULocationID, DOLocationID, SR_flag, Affiliated_num,
    fhv_trip, duration
)
SELECT
    s.TripID AS fhv_trip_id,
    l.licenseID,
    t_pick.timeID,
    t_drop.timeID,
    s.PULocationID,
    s.DOLocationID,
    s.SR_flag,
    s.Affiliated_num,
    s.fhv_trip,
    s.Duration
FROM
    [dbo].[STG_TRIPS] s
LEFT JOIN
    [dbo].[DIM_TIME] t_pick ON t_pick.[date] = s.PickupDateTime
LEFT JOIN
    [dbo].[DIM_TIME] t_drop ON t_drop.[date] = s.DropoffDateTime
LEFT JOIN
    [dbo].[DIM_LICENSE] l ON l.license_num = s.LicenseNum; -- Corrección del JOIN
GO
```

### Validaciones Realizadas

Durante el desarrollo, se revisaron los nombres de las columnas y las relaciones para garantizar la integridad de los datos y evitar inconsistencias. Las columnas adicionales y ajustes realizados están respaldados por el análisis detallado del documento _Solución PR1.pdf_.

En resumen, este script refleja la aplicación práctica de las especificaciones teóricas y garantiza un flujo ETL sólido y eficiente.

### **Verificación y Validación Final**

Después de ejecutar el script completo, debería verificar que los datos se hayan cargado correctamente en todas las tablas dimensionales y de hechos.

```sql
-- Verificar registros en DIM_LOCATION
SELECT COUNT(*) AS TotalRecords FROM [dbo].[DIM_LOCATION];
-- Verificar registros en DIM_VENDOR
SELECT COUNT(*) AS TotalRecords FROM [dbo].[DIM_VENDOR];
-- Verificar registros en DIM_PAYMENT
SELECT COUNT(*) AS TotalRecords FROM [dbo].[DIM_PAYMENT];
-- Verificar registros en DIM_RATE
SELECT COUNT(*) AS TotalRecords FROM [dbo].[DIM_RATE];
-- Verificar registros en DIM_TIME
SELECT COUNT(*) AS TotalRecords FROM [dbo].[DIM_TIME];
-- Verificar registros en DIM_LICENSE
SELECT COUNT(*) AS TotalRecords FROM [dbo].[DIM_LICENSE];
-- Verificar registros en FACT_NYTAXI_TRIP
SELECT COUNT(*) AS TotalRecords FROM [dbo].[FACT_NYTAXI_TRIP];
-- Verificar registros en FACT_FHV_TRIP
SELECT COUNT(*) AS TotalRecords FROM [dbo].[FACT_FHV_TRIP];
```

## Establecer el entorno

Para ahorrarme el paso del driver he aplicado la siguiente solución:
```.kettle.properties
# Ruta a las fuentes de datos
DIR_ENT=F:\fuentes

DB_HOST=UCS1R1UOCSQL01
DB_PORT=1433
DB_NAME=GOG
DB_USER=STUDENT_vnaranjom
```
Connection». En la creación de la conexión al «STAGE», el nombre que se les asignará es **cn_stage**:
![[Pasted image 20241219224952.png]]

En la creación de la conexión al «DW», el nombre que se le dará es **cn_dw**:
![[Pasted image 20241219225330.png]]

### **Uso de Variables de Entorno vs Cadena de Conexión Completa**

#### **Ventajas del uso de variables de entorno**

1. **Portabilidad**:
    
    - Definir valores como `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, y `DB_PASS` me permite configurar diferentes entornos (desarrollo, producción, staging) sin modificar directamente mis transformaciones o trabajos. Solo cambio el archivo `Kettle.properties`, y listo.
2. **Flexibilidad**:
    
    - Si tengo que conectarme a un servidor diferente o usar credenciales distintas, no necesito tocar la configuración dentro de Pentaho. Solo edito el archivo de variables de entorno, y todos los procesos automáticamente usarán los nuevos valores.
3. **Simplicidad sin dependencias externas**:
    
    - Al no usar cadenas de conexión completas como `jdbc:sqlserver://<host>:<port>;databaseName=<name>;user=<user>;password=<password>`, evito depender de drivers personalizados que no puedo instalar porque no soy administrador del sistema. Esto hace que mi configuración sea más sencilla y menos propensa a errores.
4. **Claridad en la diferenciación de conexiones**:
    
    - Aunque ambas conexiones (`cn_stage` y `cn_dw`) apuntan físicamente al mismo esquema en la base de datos, usar variables separadas para definirlas en Pentaho hace que su propósito quede claramente diferenciado. Por ejemplo:
        - `cn_stage` para el área intermedia.
        - `cn_dw` para la base de datos multidimensional.
5. **Seguridad**:
    
    - Las credenciales y la información sensible no están expuestas directamente en las transformaciones o trabajos. Quedan centralizadas y protegidas en el archivo `Kettle.properties`, lo que minimiza el riesgo de filtraciones.

---

### **Configuración actual: Resultado**

Gracias a las variables de entorno:

- He podido definir claramente dos conexiones lógicas (`cn_stage` y `cn_dw`), ambas apuntando al mismo esquema físico, pero con usos diferenciados en mi proceso ETL.
- No necesito instalar drivers adicionales, lo que es ideal considerando las restricciones de mi entorno.
- Mi configuración es más clara, portable, y fácil de mantener.

## Transformaciones para **STG_TAXI_ZONES**

#### Tabla de entrada
![[Pasted image 20241220115623.png]]

#### Tabla de salida
![[Pasted image 20241220120534.png]]
**Conexión de las tablas**
![[Pasted image 20241220124947.png]]

Eliminar filas con "N/A"
![[Pasted image 20241220122646.png]]

Compruebo en la base de datos que todo esta bien.
![[Pasted image 20241220125935.png]]

## Transformaciones para **STG_TRIPS**

Para resolver este problema, lo abordé de la siguiente manera:
![[Pasted image 20241220175054.png]]

1. **Identificación del problema:**
    
    - Durante la integración de los datos de los diferentes archivos `FHV_TRIP`, noté que uno de ellos (`FHV_TRIP_2024_01`) tenía el campo `PULocationID` definido como un **boolean**, mientras que en el resto de los archivos y en la tabla destino este campo debía ser un **integer**.
    - Esto generaba un conflicto al intentar unificar los flujos de datos debido a la inconsistencia en los tipos de datos.
2. **Solución paso a paso:**
    
    - **Convertí el campo `PULocationID` a un tipo de texto (String):** Usé un paso de **Select Values** para cambiar temporalmente el tipo de dato a `String`. Esto me permitió manejar los valores `N` y `null` sin errores de tipo.
    - **Reemplacé los valores booleanos por enteros:** Implementé un paso **Value Mapper** para asignar:
        - `N` → `0`
        - `null` (o cualquier valor no coincidente) → `-1` (indicando datos faltantes).
    - **Convertí el campo nuevamente a un tipo Integer:** Utilicé otro paso **Select Values** para convertir el campo de texto resultante de `Value Mapper` a un entero (`Integer`), cumpliendo así con el esquema de la tabla destino.
3. **Validación:**
    
    - Verifiqué el flujo de datos previsualizando después de cada paso para asegurarme de que las transformaciones se aplicaran correctamente.
    - Finalmente, confirmé que el campo `PULocationID` estaba unificado y en el formato correcto en todos los flujos.
4. **Conclusión:**
    
    - Este enfoque resolvió el conflicto entre los tipos de datos, lo que permitió combinar los datos de todos los archivos sin errores y cargar los resultados en la tabla destino conforme al esquema definido.

![[Pasted image 20241220175136.png]]

Paso todos la integer de longitud 15 y precisión 0 ya que es el mismo tipo de dato en Yellow_Trip_Data.

![[Pasted image 20241220182416.png]]

#### Unir los cuatro datasets.

El paso **"AddNewConstants"** es fundamental para asegurar que los datos de ambos flujos (FHV y YELLOW) tengan una estructura homogénea, lo cual es un requisito indispensable para realizar correctamente el paso de **Append Streams**.

### **Razones por las que este paso es necesario:**

1. **Unificación de Estructura**:  
    Los datos provenientes de **FHV_TRIP** no incluyen todos los campos presentes en **YELLOW_TRIP**. Este paso añade dichos campos faltantes con valores por defecto (`null` en este caso).
    
2. **Consistencia en Tipos de Datos**:  
    Al agregar estos campos, se define explícitamente su tipo de dato, longitud y precisión, asegurando que coincidan con los campos existentes en **YELLOW_TRIP**. Esto elimina errores de incompatibilidad al intentar unir los flujos.
    
3. **Estandarización de Procesos Posteriores**:  
    Asegura que cualquier transformación o análisis posterior pueda tratar los datos de ambos flujos de manera uniforme sin necesitar verificaciones adicionales o transformaciones extra.
    
4. **Evitar Errores en la Unión de Flujos**:  
    Pentaho requiere que los flujos a unir tengan los mismos campos (nombre, tipo y formato). Sin este paso, el proceso de unión arrojaría errores, ya que faltarían campos clave.
    
5. **Flexibilidad para Manejar Valores Vacíos**:  
    Al establecer valores por defecto como `null`, se preserva la capacidad de diferenciar datos ausentes de valores explícitos (como `0`), lo que es útil para análisis más precisos.
    

En resumen, este paso es crucial para garantizar la integridad y la compatibilidad de los datos al consolidar los flujos en una estructura única y manejable.

#### **Faltantes en FHV_TRIP_DATA (presentes en YELLOW_TRIP_DATA)**
![[Pasted image 20241220203230.png]]
#### **Faltantes en YELLOW_TRIP_DATA (presentes en FHV_TRIP_DATA)**
![[Pasted image 20241220203148.png]]

En la siguiente imagen se visualiza el flujo de preparación y unificación de datos provenientes de diferentes fuentes relacionadas con los registros de viajes FHV (For-Hire Vehicles) y Yellow Taxi, con el objetivo final de insertarlos en la tabla **STG_TRIPS**. El proceso fue llevado a cabo de la siguiente manera:

1. **Procesamiento de FHV_TRIP**:
    
    - Cada archivo correspondiente a los diferentes periodos de FHV (`FHV_TRIP_2023_12`, `FHV_TRIP_2023_11`, etc.) fue procesado individualmente.
    - Se normalizaron los tipos de datos mediante pasos como `toInt` y `toString` para garantizar que todas las columnas tuvieran el formato correcto.
    - Se agregaron columnas constantes necesarias (`AddNewConstants`) que no estaban presentes en los datos originales de FHV para que coincidan con el esquema de Yellow Taxi.
    - Finalmente, los datos fueron ordenados (`Sort`) para mantener consistencia en el flujo.
2. **Procesamiento de YELLOW_TRIP**:
    
    - De manera similar, los datos de Yellow Taxi de diferentes periodos (`YELLOW_TRIP_2023_12`, `YELLOW_TRIP_2023_11`, etc.) también pasaron por un proceso de enriquecimiento mediante el paso `AddNewConFromFHV`, donde se agregaron columnas para alinear su estructura con los datos de FHV.
3. **Unificación de Datos**:
    
    - Se utilizaron varios pasos de `Append streams` para combinar los datos procesados de FHV y Yellow Taxi.
    - Este proceso asegura que todas las columnas tengan el mismo orden, tipo y estructura antes de unificar los flujos.
    - Finalmente, el último paso de unificación (`Append streams 2`) generó un flujo consolidado listo para ser cargado en **STG_TRIPS**.

En resumen, este flujo de trabajo asegura que los datos de ambas fuentes estén alineados tanto en estructura como en formato, lo que permite su integración y posterior uso en el almacén de datos o procesos analíticos.
![[Pasted image 20241222124208.png]]
Configuro la tabla de salida:
![[Pasted image 20241221124507.png]]
Las transformaciones se han realizado correctamente:
![[Pasted image 20241222144453.png]]

Comprobación en la base de datos:
![[Pasted image 20241222144705.png]]

## Transformaciones para STG_VENDORS

Codígo para transformar de tsv a csv
```python
import pandas as pd
# Leer el archivo TSV
df = pd.read_csv('CURRENT_BASES.tsv', sep='\t')
# Guardar como CSV
df.to_csv('CURRENT_BASES.csv', index=False)
```

Código para eliminar el duplicado:
```python
import pandas as pd

# Cargar el archivo CSV
file_path = "CURRENT_BASES.csv" # Ruta del archivo
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
```
![[Pasted image 20241222141034.png]]
He decidido eliminar el dato duplicado en la columna **LicenseNumber** porque este campo debe ser único para garantizar la integridad de los datos. La duplicidad identificada en el registro con el valor **B02920** representaba una inconsistencia en la fuente de datos, ya que se trata de una clave primaria que, por definición, no puede repetirse en el sistema.

Eliminé uno de los registros duplicados considerando que la localización no influye en el contexto del análisis o la finalidad de este conjunto de datos. Además, mantener la duplicidad podría generar problemas en futuros procesos de integración, consultas o reportes, como errores de referencias cruzadas o cálculos incorrectos basados en datos duplicados.

Por estas razones, opté por conservar un único registro y eliminar el duplicado, asegurando así la coherencia y fiabilidad de los datos para su procesamiento posterior.

He modificado los encabezados para eliminar los espacios entre los nombres y evitar problemas:
```code
LicenseNumber,EntityName,Telephone Number,SHL Endorsed,Building,Street,City,State,Postcode,TypeOfBase,Latitude,Longitude,Date,Time,Location
```

![[Pasted image 20241222153931.png]]

Comprobación de las transformaciones en la base de datos:
![[Pasted image 20241222154019.png]]

## Transformaciones para STG_PAYMENTS

Para cargar los métodos de pago en la tabla `STG_PAYMENTS`, primero creé un archivo CSV con los datos necesarios, asegurándome de que la estructura fuera correcta, incluyendo encabezados (`PaymentTypeID` y `PaymentTypeName`) y los valores separados por comas. Utilicé Pentaho Data Integration (Spoon) para configurar una transformación: agregué un step de entrada de archivo CSV y mapeé las columnas del archivo a los campos de la tabla en la base de datos. Luego, configuré un step de salida a la tabla `STG_PAYMENTS`, conectándome a la base de datos y asegurándome de que todo estuviera correctamente alineado. Finalmente, ejecuté la transformación y validé los datos en la base de datos con una consulta SQL para confirmar que todo se había cargado correctamente. Todo funcionó como esperaba, y los datos ya están disponibles en la tabla.

![[Pasted image 20241222155514.png]]

Comprobación en la base de datos
![[Pasted image 20241222155621.png]]

## Transformaciones para STG_RATES

Convertir el `.tab` a `csv`:

```python
import csv

# Ruta del archivo original y del archivo CSV de salida
input_file = 'Rate_code.tab'
output_file = 'Rate_code.csv'

# Leer el archivo .tab y escribirlo como un archivo .csv
with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
reader = (line.strip().split('\t') for line in infile) # Leer y dividir por tabulaciones
writer = csv.writer(outfile)
# Escribir encabezados
writer.writerow(['RateID', 'RateName'])
# Escribir datos
writer.writerows(reader)
print(f"Archivo CSV generado en: {output_file}")
```

Resultado

![[Pasted image 20241222160937.png]]

Para trabajar con los datos de tarifas, primero identifiqué que el archivo `Rate_code.tab` contenía información delimitada por tabulaciones sobre los distintos tipos de tarifas utilizadas en los viajes de taxi en Nueva York. Decidí convertir este archivo en un formato CSV para facilitar su carga en la base de datos a través de Pentaho.

Escribí un script en Python que lee el archivo original, separa los campos utilizando el tabulador como delimitador, y luego guarda los datos en un archivo CSV con encabezados claros: `RateID` y `RateName`. Este script aseguró que la estructura fuera consistente y compatible con Pentaho.

Después de generar el archivo CSV, utilicé Pentaho para cargar los datos en la tabla `STG_RATES` de la base de datos. Configuré un step de entrada para leer el CSV y otro de salida para insertar los datos en la tabla correspondiente. Finalmente, validé que la carga fue exitosa ejecutando una consulta en la base de datos, donde confirmé que todos los datos estaban correctos y organizados según lo esperado.

En la foto, se puede observar que los datos quedaron correctamente cargados en la tabla `STG_RATES`. Todo el proceso se ejecutó sin inconvenientes, desde la conversión del archivo hasta la validación de los resultados.

Comprobamos resultados:
![[Pasted image 20241222161342.png]]

![[Pasted image 20241222161449.png]]


## Transformaciones para TR_DIM_LICENSE

```sql
-- Identificar filas con formatos de Time inválidos
SELECT *
FROM STG_VENDORS
WHERE 
    NOT (
        Time LIKE '[0-1][0-9]:[0-5][0-9]:[0-5][0-9]' 
        OR Time LIKE '2[0-3]:[0-5][0-9]:[0-5][0-9]'
    );
```
Resultado : 0

He corregido y ajustado las columnas `date` y `hora` en la consulta para que solo contengan los valores correspondientes a cada tipo (fecha y hora, respectivamente). Aquí está el proceso explicado:

1. **Revisamos la estructura de las tablas de origen y destino:**  
    La tabla origen (`STG_VENDORS`) tenía las columnas `Date` (tipo `DATE`) y `Time` (tipo `VARCHAR(8)`), mientras que la tabla destino (`DIM_LICENSE`) usa `datetime` para la fecha y `time(0)` para la hora.
    
2. **Modificamos el SELECT inicial para que la fecha y la hora se separaran correctamente:**  
    Usamos `CAST([Date] AS date)` para asegurarnos de que solo se guardara la parte de la fecha en la columna `date`, y `CAST([Time] AS time(0))` para extraer únicamente la hora en formato de tiempo.
    
3. **Probamos el código en Pentaho (Spoon):**  
    Ejecutamos la transformación en Pentaho para verificar que los datos fueran procesados correctamente y enviados a la tabla destino sin errores.
    
4. **Validamos los resultados en la base de datos:**  
    Al revisar la tabla destino (`DIM_LICENSE`), confirmamos que las columnas `date` y `hora` tenían los valores correctos, es decir:
    
    - `date` muestra solo la fecha (sin horas adicionales, como `00:00:00.000`).
    - `hora` contiene solo la hora (sin fechas adicionales, como `1900-01-01`).

### Código final utilizado:

```sql
SELECT 
    CAST(SUBSTRING(LicenseNumber, 2, LEN(LicenseNumber)) AS INT) AS licenseID,
    LicenseNumber AS license_num,
    EntityName AS entity_name,
    TelephoneNumber AS telephone,
    SHLEndorsed AS SHL_endorsed,
    Building AS building,
    Street AS street,
    City AS city,
    State AS state,
    Postcode AS postcode,
    TypeOfBase AS type_base,
    CAST([Date] AS date)  AS [date],        -- Sólo la parte de la fecha
    CAST([Time] AS time(0)) AS hora,        -- Sólo la parte de la hora
    Location AS location
FROM STG_VENDORS;
```

### Resultado final:

- La consulta procesó correctamente los 852 registros y los cargó en la tabla destino.
- En las herramientas utilizadas (Pentaho y SQL Server Management Studio), se verificó que los datos fueran consistentes con lo esperado.

![[Pasted image 20241222174009.png]]

![[Pasted image 20241222174035.png]]

## Transformaciones para TR_DIM_TIME

El proceso de creación y carga de la tabla `DIM_TIME` se realiza en los siguientes pasos:

---

### **Paso 1: Generación del archivo CSV `dim_time.csv`**

#### **Código Python**

```python
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

# Set para almacenar fechas y horas únicas
unique_datetimes = set()

# Procesar cada archivo CSV
for file in csv_files:
    print(f"Procesando archivo: {file}")
    try:
        # Leer el archivo con low_memory=False para evitar advertencias
        df = pd.read_csv(file, low_memory=False)

        # Identificar tipo de archivo y columnas relevantes
        if {"pickup_datetime", "dropOff_datetime"}.issubset(df.columns):  # fhv_tripdata
            pickup_times = pd.to_datetime(df["pickup_datetime"], errors="coerce").dropna()
            dropoff_times = pd.to_datetime(df["dropOff_datetime"], errors="coerce").dropna()
            unique_datetimes.update(pickup_times.tolist())
            unique_datetimes.update(dropoff_times.tolist())
        elif {"tpep_pickup_datetime", "tpep_dropoff_datetime"}.issubset(df.columns):  # yellow_tripdata
            pickup_times = pd.to_datetime(df["tpep_pickup_datetime"], errors="coerce").dropna()
            dropoff_times = pd.to_datetime(df["tpep_dropoff_datetime"], errors="coerce").dropna()
            unique_datetimes.update(pickup_times.tolist())
            unique_datetimes.update(dropoff_times.tolist())
        else:
            print(f"Archivo {file} no tiene las columnas esperadas, ignorando.")
    except Exception as e:
        print(f"Error al procesar el archivo {file}: {e}")

# Identificar y eliminar valores inválidos o nulos
unique_datetimes = {dt for dt in unique_datetimes if pd.notnull(dt)}

# Ordenar y convertir a DataFrame
records = [
    {
        "timeID": int(dt.strftime("%Y%m%d%H%M%S")),
        "year": dt.year,
        "month": dt.month,
        "day": dt.day,
        "hour": dt.hour,
        "min": dt.minute,
        "sg": dt.second,
        "date": dt,
    }
    for dt in sorted(unique_datetimes)
]

# Crear DataFrame para la tabla DIM_TIME
dim_time_df = pd.DataFrame(records)

# Guardar en un archivo CSV
dim_time_df.to_csv("dim_time.csv", index=False)
print("\nArchivo dim_time.csv generado con éxito.")
```

El código tiene como objetivo procesar múltiples archivos CSV que contienen datos de tiempo, identificar las fechas y horas únicas y generar un archivo `dim_time.csv` con una estructura adecuada para ser cargada en una base de datos.

- **Carga de datos CSV**: Se cargan archivos con diferentes estructuras (`fhv_tripdata` y `yellow_tripdata`) y se identifican las columnas relevantes de fechas y horas (`pickup_datetime`, `dropOff_datetime`, `tpep_pickup_datetime`, `tpep_dropoff_datetime`).
- **Conversión y limpieza**:
    - Se convierten las columnas identificadas a formato `datetime` utilizando `pd.to_datetime`.
    - Se descartan valores nulos o inválidos.
- **Generación de registros únicos**:
    - Se extraen los componentes de tiempo (año, mes, día, hora, minuto, segundo) y se asigna un identificador único (`timeID`) basado en el formato `YYYYMMDDHHMMSS`.
- **Exportación a CSV**: El archivo `dim_time.csv` se guarda localmente para su carga posterior.

---

### **Paso 2: Configuración en Pentaho Spoon**

#### **Configuración del flujo en Spoon** (ver **Imagen 1**)

1. **CSV File Input**:
    - Configuración para leer el archivo `dim_time.csv`.
    - Se asegura que las columnas del archivo coincidan con la estructura de la tabla destino en la base de datos.
2. **Select Values**:
    - **Imagen 2** muestra la asignación de formatos de datos en este paso.
    - Las columnas deben configurarse según los tipos en la tabla SQL:
        - `timeID`: **Numeric** con precisión `18, 0`.
        - `year`, `month`, `day`, `hour`, `min`, `sg`: **String** con longitud adecuada (`4` para `year`, `2` para las demás).
        - `date`: **Date**.
3. **Table Output**:
    - Configuración para cargar los datos en la tabla `DIM_TIME` en la base de datos SQL Server.
    - En este paso se mapea cada columna del archivo al campo correspondiente en la tabla.

---
![[Pasted image 20241223194559.png]]
### **Paso 3: Comprobación en SQL Server**

#### **Consulta de validación**

La consulta en SQL Server valida que los datos se cargaron correctamente en la tabla `DIM_TIME`:

```sql
SELECT TOP (1000) [timeID], [year], [month], [day], [hour], [min], [sg], [date]
FROM [dbo].[DIM_TIME];
```

#### **Resultado esperado**

- Los datos cargados muestran:
    - `timeID` con valores en formato `YYYYMMDDHHMMSS`.
    - Columnas `year`, `month`, `day`, `hour`, `min`, `sg` con valores en formato de cadena y con longitud consistente.
    - La columna `date` muestra valores en formato de fecha y hora (`datetime`).

---
![[Pasted image 20241223174906.png]]
### **Errores Resueltos**

1. **Conflictos de tipos de datos (`datetime2` y `numeric`)**:
    - Se aseguraron los tipos correctos en **"Select Values"** y la estructura de la tabla destino.
2. **Descartar valores inválidos**:
    - En el script de Python se verificaron y excluyeron valores `NaT` o mal formateados antes de generar el archivo CSV.

---

Este flujo asegura la correcta generación, carga y validación de datos para la tabla `DIM_TIME`, integrando procesos de limpieza y mapeo adecuado de formatos en cada etapa.

## Transformaciones para TR_DIM_RATE

El flujo en Pentaho se ejecutó correctamente, procesando y escribiendo 7 filas desde la tabla de staging `STG_RATES` a la dimensión `DIM_RATE`. Los datos en la tabla destino coinciden con lo esperado, respetando la estructura definida. Todo el proceso, desde el **Table Input** hasta la escritura, fue exitoso y sin errores. Este enfoque modular es eficiente y escalable.

### Código SQL usado en el **Table Input**

```sql
SELECT 
    CAST([RateID] AS numeric(2,0)) AS rateID,
    [RateName] AS name_rate
FROM [dbo].[STG_RATES];
```

El flujo está bien diseñado, y la carga en `DIM_RATE` fue precisa y completa.

![[Pasted image 20241222193449.png]]

![[Pasted image 20241222193537.png]]

## Transformaciones para TR_DIM_PAYMENT

**Comentario del proceso**

Ejecuté la transformación en Pentaho para poblar la dimensión `DIM_PAYMENT` desde la tabla de staging `STG_PAYMENT_TYPES`. El flujo en **Spoon** consta de tres pasos: **Table Input**, **Select Values** y **Table Output** (TR_DIM_PAYMENT). Los resultados muestran que todo se ejecutó correctamente:

1. **Table Input** procesó 6 filas desde la tabla staging.
2. **Select Values** confirmó que los datos estaban alineados con los campos esperados en la tabla destino.
3. **TR_DIM_PAYMENT** escribió las 6 filas en la tabla `DIM_PAYMENT`.

El log muestra que no hubo errores ni advertencias, lo que valida que la transformación es estable.

### Estado de la tabla `DIM_PAYMENT`

Verifiqué los datos en SQL Server, y la consulta confirma que la tabla `DIM_PAYMENT` contiene los registros esperados. Las columnas `paymentID` y `Payment_type` están correctamente pobladas. Ejemplo de datos:

- `paymentID` = 0, `Payment_type` = Credit card
- `paymentID` = 5, `Payment_type` = Voided trip

La carga fue precisa y consistente con los datos de origen.

---

### Código SQL usado en el **Table Input**

```sql
SELECT 
    CAST([PaymentTypeID] AS numeric(2,0)) AS paymentID,
    [PaymentTypeName] AS Payment_type
FROM [dbo].[STG_PAYMENT_TYPES];
```

---

En resumen, el proceso fue exitoso y la dimensión quedó bien estructurada con los datos esperados. El diseño modular y el uso del paso **Select Values** permitirán futuras extensiones o validaciones.

![[Pasted image 20241222194535.png]]

![[Pasted image 20241222194104.png]]

## Transformaciones para TR_DIM_VENDOR

**Comentario del Proceso**

Ejecuté la transformación en Pentaho para cargar la dimensión `DIM_VENDOR` desde la tabla staging `STG_VENDORS`. El flujo de la transformación consta de tres pasos: **Table Input**, **Select Values**, y **Table Output** (TR_DIM_VENDOR). Los resultados fueron satisfactorios:

1. **Table Input**: Procesó correctamente las primeras 99 filas de la tabla staging.
2. **Select Values**: Confirmó el mapeo correcto de las columnas `vendorID` y `name_vendor`.
3. **Table Output**: Escribió con éxito las 99 filas en la tabla destino `DIM_VENDOR`.

El log no reportó errores, confirmando que el proceso fue ejecutado de manera precisa y sin inconvenientes.

---

### Código SQL Utilizado en **Table Input**

```sql
SELECT TOP 99
    ROW_NUMBER() OVER (ORDER BY [LicenseNumber]) AS vendorID,
    [EntityName] AS name_vendor
FROM [dbo].[STG_VENDORS];
```

---

### Justificación de la Limitación a 99 Registros

1. **Modo Educativo**:
    
    - Limitar el número de registros a 99 tiene el propósito de mantener el ejemplo práctico y manejable, ajustándose al rango permitido por la columna `vendorID` (`numeric(2,0)`).
2. **Evitar Modificaciones de la Estructura**:
    
    - Respetar el diseño original de la tabla evita tener que alterar la estructura de la base de datos, como ampliar el tamaño de la columna `vendorID`.
3. **Simplificar la Carga**:
    
    - Trabajar con un subconjunto más pequeño facilita el enfoque en las técnicas de ETL y modelado de dimensiones, sin complicaciones relacionadas con cambios estructurales.
4. **Uso Realista en Escenarios Controlados**:
    
    - En un entorno de aprendizaje o pruebas, esta limitación es razonable para ilustrar conceptos clave de integración de datos.

---

### Resultado Verificado

Al consultar la tabla `DIM_VENDOR`, confirmé que los 99 registros fueron insertados correctamente. Cada `vendorID` es único y se asignó de manera secuencial, mientras que los nombres (`name_vendor`) corresponden a los valores esperados desde la tabla staging.

El proceso es funcional y cumple con los requisitos planteados, logrando resultados consistentes y alineados con los objetivos educativos.

![[Pasted image 20241222195231.png]]

![[Pasted image 20241222195353.png]]

## Transformaciones para TR_DIM_LOCATION

Ejecuté la transformación en Pentaho para poblar la dimensión `DIM_LOCATION` desde la tabla staging `STG_TAXI_ZONES`. El flujo constó de tres pasos: **Table Input**, **Select Values** y **Table Output** (TR_DIM_LOCATION). Los resultados fueron exitosos:

1. **Table Input**: Procesó las 263 filas de la tabla staging, confirmando que todos los datos relevantes fueron leídos correctamente.
2. **Select Values**: Mapeó adecuadamente las columnas `locationID`, `borough`, `zone` y `service_zone`.
3. **Table Output**: Escribió sin errores las 263 filas en la tabla `DIM_LOCATION`.

El log confirma que no hubo errores durante el proceso, y la transformación se completó satisfactoriamente.

---

### Código SQL Utilizado en **Table Input**

```sql
SELECT 
    CAST([LocationID] AS numeric(4,0)) AS locationID,
    [Borough] AS borough,
    [Zone] AS zone,
    [Service_zone] AS service_zone
FROM [dbo].[STG_TAXI_ZONES];
```

---

### Resultado Verificado

Consulté los datos en la tabla `DIM_LOCATION`, y los resultados son consistentes con lo esperado:

- La columna `locationID` refleja los valores de `LocationID`, convertidos al tipo `numeric(4,0)`.
- Las columnas `borough`, `zone` y `service_zone` contienen la información exacta desde la tabla staging.

Ejemplos de registros:

- **`locationID` = 1, `borough` = "EWR", `zone` = "Newark Airport", `service_zone` = "EWR"**
- **`locationID` = 4, `borough` = "Manhattan", `zone` = "Alphabet City", `service_zone` = "Yellow Zone"**

---

### Conclusión

La transformación fue ejecutada correctamente y los datos fueron poblados con precisión en la dimensión `DIM_LOCATION`.

![[Pasted image 20241222200145.png]]

![[Pasted image 20241222200227.png]]

## Transformaciones para  TR_FACT_NYTAXI_TRIP

#### **1. Preparación de los datos fuente**

Comencé con los datos en formato CSV, específicamente los archivos de viajes de taxis amarillos de Nueva York. Usé un script en Python para analizar los archivos y asegurarme de que la columna `VendorID` no tuviera valores nulos. Esto era fundamental porque `VendorID` es el criterio clave que usaría más adelante para diferenciar estos datos de otra tabla de hechos que planeo crear para los datos de FHV (For-Hire Vehicles).

El script también me ayudó a validar otros aspectos básicos, como valores únicos y posibles datos faltantes, asegurándome de que la información estuviera en buen estado antes de cargarla en la base de datos.

Script para comprobar que no existan nulos en VendorID
```python
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
```

Resultado: No tenemos ningun null en la información de `Yellow_tripdata`
![[Pasted image 20241222205909.png]]

Completar las fechas de la DIM_TIME
```sql
USE [SOURCE_vnaranjom];
GO

-- Eliminar la tabla temporal si ya existe
IF OBJECT_ID('tempdb..#missing_dates') IS NOT NULL
    DROP TABLE #missing_dates;

-- Crear tabla temporal para las fechas faltantes
CREATE TABLE #missing_dates (
    missing_date DATETIME
);

-- Insertar las fechas faltantes en la tabla temporal
INSERT INTO #missing_dates (missing_date)
SELECT DISTINCT CAST(tpep_pickup_datetime AS DATETIME) AS missing_date
FROM [dbo].[STG_TRIPS] t
WHERE CAST(tpep_pickup_datetime AS DATETIME) NOT IN (SELECT [date] FROM [dbo].[DIM_TIME]);

DECLARE @batchSize INT = 100000; -- Tamaño del lote
DECLARE @offset INT = 0;         -- Inicio del lote
DECLARE @rowCount INT;           -- Total de filas

-- Obtener el total de filas en la tabla temporal
SELECT @rowCount = COUNT(*) FROM #missing_dates;

-- Validar si hay datos para procesar
IF @rowCount = 0
BEGIN
    PRINT 'No missing dates found. Exiting.';
    DROP TABLE #missing_dates; -- Limpiar la tabla temporal
    RETURN; -- Salir del script si no hay filas
END;

-- Procesar los datos en lotes
WHILE @offset < @rowCount
BEGIN
    INSERT INTO [dbo].[DIM_TIME] ([timeID], [year], [month], [day], [hour], [min], [sg], [date])
    SELECT
        ROW_NUMBER() OVER (ORDER BY missing_date) + (SELECT ISNULL(MAX(timeID), 0) FROM [dbo].[DIM_TIME]) AS timeID,
        CAST(YEAR(missing_date) AS nchar(4)) AS [year],
        RIGHT('0' + CAST(MONTH(missing_date) AS nchar(2)), 2) AS [month],
        RIGHT('0' + CAST(DAY(missing_date) AS nchar(2)), 2) AS [day],
        RIGHT('0' + CAST(DATEPART(HOUR, missing_date) AS nchar(2)), 2) AS [hour],
        RIGHT('0' + CAST(DATEPART(MINUTE, missing_date) AS nchar(2)), 2) AS [min],
        RIGHT('0' + CAST(DATEPART(SECOND, missing_date) AS nchar(2)), 2) AS [sg],
        missing_date
    FROM #missing_dates
    ORDER BY missing_date
    OFFSET @offset ROWS FETCH NEXT @batchSize ROWS ONLY;

    SET @offset = @offset + @batchSize; -- Incrementar el offset para el siguiente lote
END;

-- Eliminar la tabla temporal
DROP TABLE #missing_dates;
```

Comprobar fechas faltantes:
```sql
SELECT DISTINCT CAST(tpep_pickup_datetime AS datetime) AS missing_date
FROM [dbo].[STG_TRIPS]
WHERE CAST(tpep_pickup_datetime AS datetime) NOT IN (SELECT [date] FROM [dbo].[DIM_TIME]);
```
---

#### **2. Carga inicial en la tabla de staging (`STG_TRIPS`)**

Después, cargué los datos procesados en una tabla staging llamada `STG_TRIPS`. Diseñé esta tabla para que actúe como un contenedor temporal de todos los datos provenientes de los archivos CSV. Aquí incluí todas las columnas necesarias para alimentar tanto la tabla de hechos como las dimensiones asociadas.

Además, implementé un filtro inicial que garantizaba que solo se cargaran registros donde `VendorID` no fuera nulo. Esto me ayudó a mantener la consistencia y evitar problemas en los pasos posteriores.

---

#### **3. Transformación y carga en la tabla de hechos**

Construí la tabla de hechos **`TR_FACT_NYTAXI_TRIP`**, que es el núcleo de este proceso. Para llenarla:

- Escribí una consulta SQL que extrae los datos desde `STG_TRIPS`, mapea las claves foráneas de las dimensiones y calcula métricas importantes como:
    
    - **Duración del viaje:** Medido en segundos usando `DATEDIFF()`.
    - **Distancia del viaje:** Tomado directamente de la tabla de staging.
    - **Montos relacionados:** Como tarifas (`fare_amount`), propinas (`tip_amount`) y otros cargos.
- Usé `CAST` para asegurar que los datos fueran convertidos a los tipos correctos y compatibles con la estructura de la tabla de hechos.
    
- Implementé un identificador único para cada viaje, `nytaxi_trip_id`, usando la función `ROW_NUMBER()`. Esto garantiza que cada registro tenga una clave única.
    

Finalmente, apliqué un filtro para asegurar que solo los registros donde `VendorID IS NOT NULL` se incluyeran en la tabla de hechos. Este filtro es crucial para diferenciar estos datos de los que planeo cargar más adelante en la tabla de hechos de FHV.

---

#### **5. Implementación en Pentaho Data Integration (PDI)**

Para automatizar este proceso, configuré una transformación en Pentaho (Spoon):

1. **Table Input:** Aquí coloqué la consulta SQL que diseñé para extraer y transformar los datos desde la tabla de staging.
2. **Select Values:** Usé este paso para ajustar las columnas seleccionadas, asegurándome de que los datos estuvieran en el formato correcto.
3. **Table Output:** Este paso carga los datos transformados directamente en la tabla de hechos `TR_FACT_NYTAXI_TRIP`.

---
![[Pasted image 20241223201511.png]]
### **Resultado final**

Con este proceso, logré llenar la tabla de hechos `TR_FACT_NYTAXI_TRIP` con datos precisos y estructurados. Ahora tengo una tabla lista para análisis, con todos los datos de los viajes de taxis amarillos diferenciados claramente gracias al `VendorID`. Este trabajo también sienta las bases para cargar los datos de FHV en su propia tabla de hechos y mantener el modelo de datos limpio y eficiente.

```sql
USE [SOURCE_vnaranjom]
GO

SELECT TOP 1
    -- Identificador único para cada viaje
    ROW_NUMBER() OVER (ORDER BY tpep_pickup_datetime) AS nytaxi_trip_id,

    -- Llaves foráneas de las dimensiones
    CAST(t.[VendorID] AS numeric(2,0)) AS vendorID,
    CAST(pickup_time.timeID AS numeric(18,0)) AS pickup_datetimeID,
    CAST(dropoff_time.timeID AS numeric(18,0)) AS dropoff_datetimeID,
    CAST(t.[RatecodeID] AS numeric(2,0)) AS rateID,
    CAST(pu_loc.locationID AS numeric(4,0)) AS PULocationID,
    CAST(do_loc.locationID AS numeric(4,0)) AS DOLocationID,
    CAST(t.[payment_type] AS numeric(2,0)) AS paymentID,

    -- Campos adicionales
    t.[store_and_fwd_flag] AS IsStoredAndForwarded,
    CAST(t.[extra] AS numeric(15,2)) AS extra,
    CAST(t.[mta_tax] AS numeric(15,2)) AS mta_tax,
    CAST(t.[tip_amount] AS numeric(15,2)) AS tip_amount,
    CAST(t.[tolls_amount] AS numeric(15,2)) AS tolls_amount,
    CAST(t.[improvement_surcharge] AS numeric(15,2)) AS improvement_surcharge,
    CAST(t.[congestion_surcharge] AS numeric(15,2)) AS congestion_surcharge,
    CAST(t.[Airport_fee] AS numeric(15,2)) AS airport_free,
    CAST(t.[trip_distance] AS numeric(15,2)) AS distance,
    CAST(t.[passenger_count] AS numeric(15,0)) AS passenger,
    CAST(DATEDIFF(SECOND, t.tpep_pickup_datetime, t.tpep_dropoff_datetime) AS numeric(18,0)) AS duration,
    CAST(t.[fare_amount] AS numeric(15,2)) AS fare_amount,
    CAST(t.[total_amount] AS numeric(15,2)) AS total_amount

FROM 
    [dbo].[STG_TRIPS] t
LEFT JOIN [dbo].[DIM_VENDOR] v
    ON t.[VendorID] = v.[vendorID]
LEFT JOIN [dbo].[DIM_TIME] pickup_time
    ON CAST(t.[tpep_pickup_datetime] AS datetime) = pickup_time.[date]
LEFT JOIN [dbo].[DIM_TIME] dropoff_time
    ON CAST(t.[tpep_dropoff_datetime] AS datetime) = dropoff_time.[date]
LEFT JOIN [dbo].[DIM_LOCATION] pu_loc
    ON t.[PULocationID] = pu_loc.[locationID]
LEFT JOIN [dbo].[DIM_LOCATION] do_loc
    ON t.[DOLocationID] = do_loc.[locationID]
LEFT JOIN [dbo].[DIM_PAYMENT] p
    ON t.[payment_type] = p.[PaymentID]
LEFT JOIN [dbo].[DIM_RATE] r
    ON t.[RatecodeID] = r.[rateID]

-- Filtro para registros con VendorID no nulo
WHERE t.[VendorID] IS NOT NULL;
```

Durante el proceso de carga de datos en la tabla `FACT_NYTAXI_TRIP`, identifiqué un problema relacionado con el diseño de la estructura de la tabla, específicamente en los campos `extra`, `mta_tax`, `tip_amount`, `tolls_amount`, `improvement_surcharge`, `congestion_surcharge` y `airport_free`. Estos campos fueron definidos como `char(1)`, lo cual no es adecuado para almacenar los datos numéricos con decimales que se están procesando desde la fuente.

### **Problema identificado**

El error principal surgió al intentar insertar valores numéricos (por ejemplo, `1.750000`) en columnas que están configuradas como cadenas de texto de un solo carácter (`char(1)`). Esto generó un conflicto de tipo, resultando en el siguiente mensaje de error: **"Error de desbordamiento aritmético para el tipo varchar, valor = 1.750000."**

Tras analizar el origen del problema, concluí que la definición de estos campos como `char(1)` no está alineada con la naturaleza de los datos que se pretende almacenar. Los valores numéricos con decimales, como los impuestos y tarifas, requieren un tipo de datos numérico, como `numeric(p, s)` o `float`.

---

### **Solución aplicada**

Para resolver el problema, planteé dos posibles soluciones:

#### **1. Modificar la estructura de la tabla `FACT_NYTAXI_TRIP`**

Propuse ajustar los tipos de datos de los campos mencionados para que reflejen correctamente la naturaleza de los datos. Esto se llevó a cabo mediante las siguientes instrucciones SQL:

```sql
ALTER TABLE [dbo].[FACT_NYTAXI_TRIP]
ALTER COLUMN [extra] numeric(15, 2);

ALTER TABLE [dbo].[FACT_NYTAXI_TRIP]
ALTER COLUMN [mta_tax] numeric(15, 2);

ALTER TABLE [dbo].[FACT_NYTAXI_TRIP]
ALTER COLUMN [tip_amount] numeric(15, 2);

ALTER TABLE [dbo].[FACT_NYTAXI_TRIP]
ALTER COLUMN [tolls_amount] numeric(15, 2);

ALTER TABLE [dbo].[FACT_NYTAXI_TRIP]
ALTER COLUMN [improvement_surcharge] numeric(15, 2);

ALTER TABLE [dbo].[FACT_NYTAXI_TRIP]
ALTER COLUMN [congestion_surcharge] numeric(15, 2);

ALTER TABLE [dbo].[FACT_NYTAXI_TRIP]
ALTER COLUMN [airport_free] numeric(15, 2);
```

Esta solución permitió que las columnas aceptaran valores numéricos con hasta 15 dígitos y 2 decimales, resolviendo el conflicto de tipos.

#### **2. Ajustar la transformación de datos (opcional)**

En caso de no poder modificar la estructura de la tabla destino, planteé una alternativa para ajustar el SQL de inserción. Este enfoque implica redondear los valores numéricos a enteros y convertirlos en cadenas de un solo carácter (`char(1)`). Aunque esta opción resolvía el problema técnico, la descarté debido a la pérdida de precisión en los datos, lo que no es ideal en un sistema de análisis.

---

### **Recomendación final**

Implementé la primera solución, modificando la estructura de la tabla para que los tipos de datos sean consistentes con la naturaleza de los valores a almacenar. Este enfoque no solo resolvió el problema inmediato, sino que también asegura una mejor alineación con las buenas prácticas de diseño de bases de datos, evitando errores similares en futuras cargas.

---

### **Lección aprendida**

Este caso resalta la importancia de alinear el diseño de la base de datos con la naturaleza de los datos que se procesarán. Definir correctamente los tipos de datos desde el principio no solo mejora la integridad de los datos, sino que también reduce el tiempo necesario para resolver problemas durante la integración.
## Transformaciones para  TR_FACT_FHV_TRIP

Para llenar la tabla de hechos `FACT_FHV_TRIP`, aproveché todas las validaciones y comprobaciones que ya realicé previamente para la tabla de taxis amarillos (`FACT_NYTAXI_TRIP`). Este proceso fue más sencillo porque ya tenía las dimensiones listas y estructuradas.

1. **Diseñé el flujo en Pentaho**:
    
    - Usé un componente `Table Input` donde coloqué la consulta SQL que filtra solo los registros con `VendorID IS NULL` desde la tabla staging `STG_TRIPS`.
    - En el paso `Select Values`, ajusté las columnas para que coincidan con los campos de la tabla de hechos, asegurándome de mapear correctamente las claves foráneas y las métricas, como `duration`.
2. **Estructura del flujo**:
    
    - Extraje los datos de `STG_TRIPS`, los procesé, y luego los dirigí hacia la salida (`Table Output`) para preparar la carga final.
3. **Resultado**:
    
    - Este flujo generó los datos listos para la tabla `FACT_FHV_TRIP`, diferenciándola claramente de los taxis amarillos gracias al filtro de `VendorID IS NULL`. Fue rápido y eficiente porque reutilicé la lógica ya validada.
    
```sql
SELECT
    ROW_NUMBER() OVER (ORDER BY t.tpep_pickup_datetime) AS fhv_trip_id,

    l.licenseID AS licenseID,
    pickup_time.timeID AS pickup_datetimeID,
    dropoff_time.timeID AS dropoff_datetimeID,
    pu_loc.locationID    AS PULocationID,
    do_loc.locationID    AS DOLocationID,
    t.SR_Flag            AS SR_flag,

    -- En lugar de CAST..., hacemos el JOIN y tomamos aff.licenseID
    aff.licenseID        AS Affiliated_num,

    NULL AS fhv_trip,
    CAST(DATEDIFF(SECOND, t.tpep_pickup_datetime, t.tpep_dropoff_datetime) AS numeric(18,0)) AS duration

FROM [dbo].[STG_TRIPS] t

-- JOIN principal para 'dispatching_base_num'
LEFT JOIN [dbo].[DIM_LICENSE] l
    ON 'B' + RIGHT(
         REPLICATE('0',5) + LTRIM(RTRIM(t.dispatching_base_num)), 
         5
       ) = l.license_num

-- JOIN para 'Affiliated_base_number'
LEFT JOIN [dbo].[DIM_LICENSE] aff
    ON 'B' + RIGHT(
         REPLICATE('0',5) + LTRIM(RTRIM(t.Affiliated_base_number)), 
         5
       ) = aff.license_num

-- JOIN con DIM_TIME
LEFT JOIN [dbo].[DIM_TIME] pickup_time
    ON CAST(t.tpep_pickup_datetime AS datetime) = pickup_time.[date]

LEFT JOIN [dbo].[DIM_TIME] dropoff_time
    ON CAST(t.tpep_dropoff_datetime AS datetime) = dropoff_time.[date]

-- JOIN con DIM_LOCATION
LEFT JOIN [dbo].[DIM_LOCATION] pu_loc
    ON t.PULocationID = pu_loc.locationID

LEFT JOIN [dbo].[DIM_LOCATION] do_loc
    ON t.DOLocationID = do_loc.locationID

WHERE 
    t.VendorID IS NULL
    AND t.dispatching_base_num IS NOT NULL
    AND t.dispatching_base_num != ''
    -- Filtramos registros donde NO haya licencia de dispatch:
    AND l.licenseID IS NOT NULL
    -- Filtramos registros donde NO haya licencia afiliada (si es obligatorio):
    AND aff.licenseID IS NOT NULL;
 
```

![[Pasted image 20241223235313.png]]

![[Pasted image 20241223230438.png]]
# Creación de JOBS

#### JOB_IN_TAXIS_ZONE
![[Pasted image 20241220130046.png]]
**Comentario sobre la Ejecución del Job: `JOB_IN_TAXI_ZONES`**

La ejecución del Job `JOB_IN_TAXI_ZONES` muestra resultados exitosos en todas las etapas, como se detalla en los logs de ejecución:

1. **Inicio del Job**:
    
    - El Job inició correctamente a las `12:56:28`, indicando que todas las configuraciones iniciales estaban adecuadamente establecidas.
2. **Paso `Start`**:
    
    - Este paso inicializa el flujo del Job, confirmando que no hay errores en la configuración general del mismo.
3. **Transformación `IN_TAXI_ZONES`**:
    
    - La transformación principal del Job, que lee y carga los datos desde el archivo fuente `taxi_zone_lookup.csv` a la tabla `STG_TAXI_ZONES`, se completó con éxito.
    - No se encontraron errores durante la ejecución de este paso, lo que indica que el archivo fuente y los mapeos entre campos están correctamente definidos.
4. **Paso `Success`**:
    
    - Este paso finalizó el Job, confirmando que todas las operaciones previas se ejecutaron sin problemas y que el flujo general del Job concluyó como estaba planeado.
5. **Resultado General**:
    
    - El estado final del Job es **Success**, lo que valida que los datos fueron procesados y cargados correctamente en el almacén intermedio (`STG`).

#### Compruebo en la base de datos
![[Pasted image 20241220130215.png]]

#### JOB_IN_TRIPS
Este es el **job maestro** que diseñé para orquestar la ejecución de las transformaciones relacionadas con los viajes (`TR_IN_TRIPS`). El flujo inicia con un paso de **inicio (`Start`)**, que asegura que todas las dependencias estén listas. Luego, se ejecuta la transformación principal `TR_IN_TRIPS`, que integra los datos necesarios para las tablas de hechos. Finalmente, el proceso termina con un paso de **éxito (`Success`)** que marca el job como completado correctamente.

Este diseño asegura que todo se ejecute en orden y sin errores, permitiendo una gestión centralizada y eficiente de las transformaciones relacionadas con los datos de viajes.
![[Pasted image 20241223204016.png]]

#### JOB_IN_VENDORS

En este caso, el **job maestro `JOB_IN_VENDORS`** se utiliza para gestionar la ejecución de la transformación relacionada con la carga de datos de proveedores (`TR_IN_VENDORS`).

1. **Inicio (`Start`)**: Este paso asegura que el proceso comience solo cuando todas las dependencias necesarias estén disponibles y listas.
    
2. **Transformación (`TR_IN_VENDORS`)**: Aquí se ejecuta la transformación que procesa los datos de los proveedores, mapeando y transformando los datos según las dimensiones y requisitos definidos.
    
3. **Finalización (`Success`)**: Este paso valida que todo el flujo se haya ejecutado correctamente y marca el job como exitoso.
    

Con este flujo simple pero efectivo, garantizo que los datos de proveedores sean procesados de manera autónoma y sin errores, siguiendo la misma lógica modular que en los otros jobs.

![[Pasted image 20241223204250.png]]

#### JOB_IN_PAYMENTS

En este caso, el **job `JOB_IN_PAYMENTS`** sigue el mismo patrón que los jobs anteriores, pero está enfocado en la carga y procesamiento de los datos relacionados con los métodos de pago.

1. **Inicio (`Start`)**:
    
    - Este paso asegura que el proceso comience de manera controlada, verificando que el flujo esté listo para ejecutarse.
2. **Transformación (`TR_IN_PAYMENTS`)**:
    
    - Aquí se realiza el procesamiento de los datos de métodos de pago. Se extraen, transforman y ajustan los datos desde la fuente para que encajen correctamente en la tabla de dimensión correspondiente.
3. **Finalización (`Success`)**:
    
    - Este paso valida que el job haya terminado con éxito, marcándolo como completo y sin errores.

Con este flujo modular, se garantiza que los datos de métodos de pago sean procesados y cargados correctamente, siguiendo una estructura clara y reutilizable en el ETL.

![[Pasted image 20241223204551.png]]
#### JOB_IN_RATES

Este es el **job `JOB_IN_RATES`**, diseñado para manejar la carga y transformación de datos relacionados con las tarifas (`TR_IN_RATES`).

1. **Inicio (`Start`)**:
    
    - Marca el inicio del proceso, asegurando que todos los elementos necesarios estén en orden para ejecutar la transformación.
2. **Transformación (`TR_IN_RATES`)**:
    
    - Este paso procesa los datos de tarifas, ajustándolos para que cumplan con la estructura y requisitos de la tabla de dimensión de tarifas. Aquí se realizan las conversiones y mapeos necesarios.
3. **Finalización (`Success`)**:
    
    - Indica que el proceso ha sido exitoso, confirmando que todos los datos fueron procesados sin errores.

El flujo es simple pero efectivo, garantizando que las tarifas sean procesadas correctamente y que el pipeline ETL mantenga su integridad y consistencia.

![[Pasted image 20241223204741.png]]

#### JOB_TR_DIM_LOCATION

Este es el **job `JOB_TR_DIM_LOCATION`**, que se encarga de la carga y transformación de datos relacionados con la dimensión de ubicaciones.

1. **Inicio (`Start`)**:
    
    - Este paso inicia el proceso y verifica que todo esté listo para ejecutar la transformación.
2. **Transformación (`TR_DIM_LOCATION`)**:
    
    - Aquí se procesan los datos de ubicaciones, transformándolos y mapeándolos para que coincidan con la estructura de la tabla de dimensión `DIM_LOCATION`. Esto incluye la validación de datos, asignación de claves y ajuste de formatos.
3. **Finalización (`Success`)**:
    
    - Este paso marca el final del proceso y confirma que la transformación se ejecutó correctamente sin errores.

Este flujo garantiza que la dimensión de ubicaciones sea construida y cargada de manera eficiente, asegurando que los datos estén listos para ser usados en los análisis posteriores.

![[Pasted image 20241223205200.png]]

#### JOB_TR_DIM_VENDOR

Este es el **job `JOB_TR_DIM_VENDOR`**, utilizado para la carga y transformación de datos relacionados con los conductores (`DIM_VENDOR`).

1. **Inicio (`Start`)**:
    
    - Se asegura de que el proceso comience correctamente, verificando que todo esté preparado antes de la ejecución.
2. **Transformación (`TR_DIM_VENDOR`)**:
    
    - Este paso realiza la transformación de los datos de proveedores, validando y mapeando la información necesaria para que cumpla con la estructura de la tabla `DIM_VENDOR`. Aquí se procesan las claves y los datos relacionados con los nombres de los proveedores.
3. **Finalización (`Success`)**:
    
    - Este paso confirma que la transformación fue exitosa y que los datos están listos para ser utilizados en las tablas de hechos u otras dimensiones.

Con este flujo modular, garantizo que los datos de los proveedores se procesen de forma correcta y eficiente, asegurando la calidad de los datos para su posterior análisis.

![[Pasted image 20241223205602.png]]
#### JOB_TR_DIM_PAYMENT

Este es el **job `JOB_TR_DIM_PAYMENT`**, diseñado para manejar la carga y transformación de la dimensión relacionada con los métodos de pago.

1. **Inicio (`Start`)**:
    
    - Este paso marca el inicio del proceso, asegurándose de que todo esté listo antes de proceder con la transformación.
2. **Transformación (`TR_DIM_PAYMENT`)**:
    
    - Aquí se procesan los datos relacionados con los métodos de pago. La transformación valida y ajusta los datos para que coincidan con la estructura de la tabla de dimensión `DIM_PAYMENT`, asignando correctamente claves y ajustando formatos si es necesario.
3. **Finalización (`Success`)**:
    
    - Indica que el proceso ha sido completado correctamente, asegurando que los datos de los métodos de pago estén listos y sin errores.

Con este flujo, la dimensión de métodos de pago se gestiona de forma eficiente, permitiendo que los datos estén disponibles para su uso en las tablas de hechos.

![[Pasted image 20241223205346.png]]

#### JOB_TR_DIM_RATE

Este es el **job `JOB_TR_DIM_RATE`**, encargado de la carga y transformación de datos para la dimensión de tarifas (`DIM_RATE`).

1. **Inicio (`Start`)**:
    
    - Marca el inicio del proceso, asegurando que todas las condiciones previas estén listas antes de ejecutar la transformación.
2. **Transformación (`TR_DIM_RATE`)**:
    
    - En este paso, se procesan los datos relacionados con las tarifas. Aquí se validan y transforman los registros para adaptarlos a la estructura de la tabla `DIM_RATE`, asegurando que los datos sean consistentes y estén correctamente formateados.
3. **Finalización (`Success`)**:
    
    - Indica que el proceso se completó con éxito, garantizando que los datos de tarifas están listos para ser utilizados en análisis o integrados en las tablas de hechos.

Este flujo es fundamental para que la dimensión de tarifas esté correctamente cargada y disponible para su uso en el modelo de datos.

![[Pasted image 20241223205847.png]]
#### JOB_TR_DIM_TIME

Este es el **job `JOB_TR_DIM_TIME`**, encargado de procesar y cargar la dimensión de tiempo (`DIM_TIME`).

1. **Inicio (`Start`)**:
    
    - Este paso asegura que el proceso comience de manera ordenada, verificando que todas las condiciones iniciales estén listas para la ejecución.
2. **Transformación (`TR_DIM_TIME`)**:
    
    - Aquí se procesan los datos relacionados con fechas y tiempos. La transformación genera los registros necesarios, desglosando los componentes de fecha y hora (año, mes, día, hora, minuto, segundo) y los ajusta a la estructura de la tabla `DIM_TIME`. Esto permite análisis temporales detallados.
3. **Finalización (`Success`)**:
    
    - Este paso valida que el proceso se haya completado correctamente, marcando el job como exitoso y asegurando que los datos de la dimensión de tiempo estén listos para su uso.

Este flujo es esencial para garantizar que la dimensión de tiempo esté correctamente estructurada y disponible para el análisis en las tablas de hechos.

![[Pasted image 20241223210026.png]]
#### JOB_TR_DIM_LICENSE

Este es el **job `JOB_TR_DIM_LICENSE`**, encargado de la carga y transformación de datos relacionados con la dimensión de licencias (`DIM_LICENSE`).

1. **Inicio (`Start`)**:
    
    - Este paso inicial asegura que el proceso comience correctamente, validando que todo esté preparado para la transformación.
2. **Transformación (`TR_DIM_LICENSE`)**:
    
    - En este paso, se procesan los datos de licencias. La transformación valida y ajusta los datos para que coincidan con la estructura de la tabla `DIM_LICENSE`, garantizando que los registros sean consistentes y se asignen correctamente las claves de licencia y otros detalles asociados.
3. **Finalización (`Success`)**:
    
    - Este paso marca que el proceso se completó exitosamente, asegurando que los datos de la dimensión de licencias estén listos para integrarse en las tablas de hechos y análisis posteriores.

Con este flujo modular, los datos de licencias son procesados eficientemente, asegurando su calidad y disponibilidad para el modelo de datos.

![[Pasted image 20241223210302.png]]

#### JOB_TR_FACT_NYTAXI_TRIP

Este es el **job `JOB_TR_FACT_NYTAXI_TRIP`**, diseñado para procesar y cargar los datos en la tabla de hechos `FACT_NYTAXI_TRIP`.

1. **Inicio (`Start`)**:
    
    - Marca el inicio del proceso, verificando que todas las dependencias estén listas antes de proceder con la transformación.
2. **Transformación (`TR_FACT_NYTAXI_TRIP`)**:
    
    - En este paso, se procesan los datos de viajes de taxis amarillos. La transformación combina información de las dimensiones relacionadas (ubicación, tiempo, proveedor, entre otras) y calcula métricas clave como duración, distancia y montos. Esto asegura que los datos estén listos y correctamente estructurados para la tabla de hechos.
3. **Finalización (`Success`)**:
    
    - Este paso confirma que el proceso se completó exitosamente, indicando que los datos se cargaron correctamente en la tabla de hechos.

Con este flujo, los datos de los viajes de taxis amarillos se integran de manera eficiente, proporcionando una base sólida para análisis y reportes posteriores.

![[Pasted image 20241223210541.png]]

#### JOB_TR_FACT_FHV_TRIP

Este es el **job `JOB_TR_FACT_FHV_TRIP`**, diseñado para procesar y cargar los datos en la tabla de hechos `FACT_FHV_TRIP`.

1. **Inicio (`Start`)**:
    
    - Marca el comienzo del proceso, verificando que todas las condiciones necesarias estén listas para ejecutar la transformación.
2. **Transformación (`TR_FACT_FHV_TRIP`)**:
    
    - En este paso, se procesan los datos correspondientes a los viajes de FHV (For-Hire Vehicles). La transformación filtra los registros donde `VendorID` es nulo, mapea las claves de las dimensiones (tiempo, ubicación, licencias) y calcula métricas como la duración del viaje. Esto asegura que los datos estén listos para su integración en la tabla de hechos.
3. **Finalización (`Success`)**:
    
    - Este paso confirma que la transformación fue completada exitosamente y que los datos fueron preparados y estructurados adecuadamente.

Con este flujo, los datos de los viajes de FHV se integran de manera eficiente en la tabla de hechos, permitiendo análisis y reportes específicos para esta categoría de viajes.

![[Pasted image 20241223210723.png]]