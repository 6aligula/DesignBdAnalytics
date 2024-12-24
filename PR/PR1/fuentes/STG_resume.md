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