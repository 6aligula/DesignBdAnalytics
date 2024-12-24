USE [SOURCE_vnaranjom]
GO

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

-- Procesar los datos en lotes
WHILE @offset < @rowCount
BEGIN
    INSERT INTO [dbo].[DIM_TIME] ([timeID], [year], [month], [day], [hour], [min], [sg], [date])
    SELECT
        ROW_NUMBER() OVER (ORDER BY missing_date) + (SELECT ISNULL(MAX(timeID), 0) FROM [dbo].[DIM_TIME]) AS timeID,
        YEAR(missing_date) AS [year],
        RIGHT('0' + CAST(MONTH(missing_date) AS NVARCHAR), 2) AS [month],
        RIGHT('0' + CAST(DAY(missing_date) AS NVARCHAR), 2) AS [day],
        RIGHT('0' + CAST(DATEPART(HOUR, missing_date) AS NVARCHAR), 2) AS [hour],
        RIGHT('0' + CAST(DATEPART(MINUTE, missing_date) AS NVARCHAR), 2) AS [min],
        RIGHT('0' + CAST(DATEPART(SECOND, missing_date) AS NVARCHAR), 2) AS [sg],
        missing_date
    FROM #missing_dates
    ORDER BY missing_date
    OFFSET @offset ROWS FETCH NEXT @batchSize ROWS ONLY;

    SET @offset = @offset + @batchSize; -- Incrementar el offset para el siguiente lote
END;




