USE [master]
GO

ALTER DATABASE [dbwins_demo] SET CHANGE_TRACKING = ON 
GO

ALTER DATABASE [dbwins_demo] SET CHANGE_TRACKING (CHANGE_RETENTION = 1 HOURS)
GO

USE [dbwins_demo]
GO

ALTER TABLE [dbo].[EMVendor] ENABLE CHANGE_TRACKING WITH(TRACK_COLUMNS_UPDATED = ON)
GO

ALTER TABLE [dbo].[EMGood] ENABLE CHANGE_TRACKING 
GO


/****** Stored Procedures api_getchangedtablename ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

CREATE PROCEDURE api_getchangedtablename
	@CurrentVersion INT = NULL
AS
BEGIN
	-- SET NOCOUNT ON added to prevent extra result sets from interfering with SELECT statements.
	SET NOCOUNT ON

	DECLARE @ControlVersionNo INT = @CurrentVersion
	--DECLARE @@ControlVersionNo INT = CHANGE_TRACKING_CURRENT_VERSION() - 1

	DECLARE @trackedTables AS TABLE ([NAME] NVARCHAR(1000))
	INSERT INTO @trackedTables ([NAME])
	SELECT	[sys].[tables].[name]
	FROM	[sys].[change_tracking_tables] 
	JOIN	[sys].[tables] ON [tables].[object_id] = [change_tracking_tables].[object_id]

	DECLARE @changedTables AS TABLE ([NAME] NVARCHAR(1000))
	DECLARE @tableName NVARCHAR(1000)
	WHILE EXISTS (SELECT TOP 1 * FROM @trackedTables)
	BEGIN
	  SET @tableName = (SELECT TOP 1 [NAME] FROM @trackedTables ORDER BY [NAME] ASC)
	  DECLARE @sql NVARCHAR(250)
	  DECLARE @retVal INT 
	  SET @sql = 'SELECT @retVal = COUNT(*) FROM changetable(changes ' + @tableName + ', ' + cast(@ControlVersionNo AS VARCHAR) + ') AS changedTable'
	  EXEC sp_executesql @sql, N'@retVal INT OUTPUT', @retVal OUTPUT
  
	  IF @retval > 0
	  BEGIN
		INSERT INTO @changedTables ([NAME]) SELECT @tableName
	  END
	  DELETE FROM @trackedTables WHERE [NAME] = @tableName  
	END

	SELECT * FROM @changedTables
END
GO


/****** Stored Procedures api_getchangedset ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

CREATE PROCEDURE api_getchangedset
	@CurrentVersion INT = NULL
AS
BEGIN
	-- SET NOCOUNT ON added to prevent extra result sets from interfering with SELECT statements.
	SET NOCOUNT ON

	DECLARE @ControlVersionNo INT = @CurrentVersion

	DECLARE @trackedTables AS TABLE ([NAME] NVARCHAR(1000))
	INSERT INTO @trackedTables ([NAME])
	EXEC [api_getchangedtablename]
		 @CurrentVersion = @ControlVersionNo

    DECLARE @changedTables AS TABLE ([VERSION] INT, [OPERATION] NVARCHAR(10), [TABLE] NVARCHAR(MAX), [COL_ID] NVARCHAR(MAX), [ID] NVARCHAR(MAX))
	DECLARE @tableName NVARCHAR(1000)
	DECLARE @columnName NVARCHAR(1000)
	WHILE EXISTS (SELECT TOP 1 * FROM @trackedTables)
	BEGIN
	  DECLARE @sql NVARCHAR(MAX)
	  DECLARE @retVal INT

	  SET @tableName = (SELECT TOP 1 [NAME] FROM @trackedTables)
	  SET @sql = 'SELECT CT.* FROM CHANGETABLE (CHANGES [' + @tableName + '], ' + cast(@ControlVersionNo AS VARCHAR) + ') AS CT'
	  SET @columnName = (	SELECT TOP 1 [NAME]
							FROM sys.dm_exec_describe_first_result_set
							(@sql, NULL, 0)
							WHERE [NAME] NOT LIKE ('SYS_%')
						 )

	  SET @sql = 'SELECT CT.SYS_CHANGE_VERSION, CT.SYS_CHANGE_OPERATION, ''[' + @tableName + ']'', ''[' + @columnName + ']'' AS COL_ID, CT.[' + @columnName +'] AS ID
			      FROM CHANGETABLE (CHANGES [' + @tableName + '],' + cast(@ControlVersionNo AS VARCHAR) + ') AS CT'
	
	  PRINT(@sql)
	  INSERT INTO @changedTables 
	  EXECUTE sp_executesql @sql

	  DELETE FROM @trackedTables WHERE [NAME] = @tableName
	END

	SELECT * FROM @changedTables
END
GO