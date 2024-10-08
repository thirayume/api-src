USE [dbwins_demo]
GO

/****** Stored Procedures api_sendrequest ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

ALTER PROCEDURE api_sendrequest
	@Operation CHAR(1),
	@Url NVARCHAR(400),
	@JsonData NVARCHAR(MAX) = NULL
AS
BEGIN
	-- SET NOCOUNT ON added to prevent extra result sets from
	-- interfering with SELECT statements.
	SET NOCOUNT ON;

	DECLARE @Cmd NVARCHAR(4000) 
	SET @Cmd = 'python C:\ws-api\trigger_api.py '

	-- Only execute if URL is defined
	IF @Url IS NOT NULL 
	BEGIN
		IF @JsonData IS NOT NULL 
		BEGIN
			SET @JsonData = REPLACE(@JsonData, '"', '\"')
			SET @JsonData = REPLACE(@JsonData, ' ', '')
			PRINT ('"' + @JsonData + '"')
			SET @Cmd = @Cmd + @Operation + ' ' + @Url + ' ' + @JsonData
		END
		ELSE
		BEGIN
			SET @Cmd = @Cmd + @Operation + ' ' + @Url
		END

		SET @Cmd = @Cmd + ' timeout /t 30'
		--PRINT(@Cmd)
		EXEC xp_cmdshell @Cmd;
	END
END
GO

/****** Trigger [trg_API_Vendors] ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

ALTER TRIGGER [dbo].[trg_API_Vendors]
ON [dbo].[EMVendor]
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
	DECLARE @JsonData NVARCHAR(MAX)
	DECLARE @Url NVARCHAR(400)
	DECLARE @VendorID INT
	DECLARE @Operation CHAR(1)

	DECLARE @BaseUrl NVARCHAR(255) 
	SET @BaseUrl = 'http://localhost:8000/vendors/'
	--SET @BaseUrl = 'https://intergroup.odoothaicloud.com/web/api/vendor'
	DECLARE @DbNum CHAR(1)
	SET @DbNum = '2'

	-- Check if rows were deleted
	IF NOT EXISTS(SELECT * from INSERTED) AND EXISTS (SELECT * from DELETED)
    BEGIN
        SET @Operation = 'D'
		PRINT(@Operation)

        -- Use a cursor to iterate over deleted rows
        DECLARE deleted_cursor CURSOR FOR
            SELECT VendorID FROM DELETED

        OPEN deleted_cursor
        FETCH NEXT FROM deleted_cursor INTO @VendorID

        WHILE @@FETCH_STATUS = 0
        BEGIN
            SET @Url = @BaseUrl + 'del/' + CAST(@VendorID AS NVARCHAR(50)) + '?dbNum=' + @DbNum -- Specify DELETE URL

			EXEC api_sendrequest @Operation, @Url, NULL
            
			FETCH NEXT FROM deleted_cursor INTO @VendorID
        END

        CLOSE deleted_cursor
        DEALLOCATE deleted_cursor
    END

	-- Check if rows were inserted
	IF EXISTS(SELECT * from INSERTED) AND NOT EXISTS (SELECT * from DELETED)
	BEGIN
		--SET @VendorID = (SELECT VendorID FROM INSERTED)
		SET @Operation = 'I'
		PRINT(@Operation)

		-- Use a cursor to iterate over deleted rows
		DECLARE inserted_cursor CURSOR FOR
			SELECT VendorID FROM INSERTED

		OPEN inserted_cursor
		FETCH NEXT FROM inserted_cursor INTO @VendorID

		WHILE @@FETCH_STATUS = 0
		BEGIN
			SET @Url = @BaseUrl + 'new?dbNum=' + @DbNum  -- Specify INSERT URL
			--SET @Url = @BaseUrl + ''

			-- Construct JSON data based on the current row
			-- Construct JSON data based on the current row
			SET @JsonData =	(SELECT 
							'"' + 'VendorID' + '":"' + ISNULL(CAST([VendorID] AS NVARCHAR(MAX)), '') + '",' +
							'"' + 'VendorTitle' + '":"' + ISNULL([VendorTitle], '') + '",' +
							'"' + 'VendorName' + '":"' + ISNULL([VendorName], '') + '",' +
							'"' + 'VendorNameEng' + '":"' + ISNULL([VendorNameEng], '') + '",' +
							'"' + 'ShortName' + '":"' + ISNULL([ShortName], '') + '",' +
							'"' + 'VendorCode' + '":"' + ISNULL([VendorCode], '') + '",' +
							'"' + 'VendorType' + '":"' + ISNULL([VendorType], '') + '",' +
							'"' + 'VendorAddr1' + '":"' + ISNULL([VendorAddr1], '') + '",' +
							'"' + 'VendorAddr2' + '":"' + ISNULL([VendorAddr2], '') + '",' +
							'"' + 'District' + '":"' + ISNULL([District], '') + '",' +
							'"' + 'Amphur' + '":"' + ISNULL([Amphur], '') + '",' +
							'"' + 'Province' + '":"' + ISNULL([Province], '') + '",' +
							'"' + 'PostCode' + '":"' + ISNULL([PostCode], '') + '",' +
							'"' + 'TaxId' + '":"' + ISNULL([TaxId], '') + '",' +
							'"' + 'ContTel' + '":"' + ISNULL([ContTel], '') + '",' +
							'"' + 'ContFax' + '":"' + ISNULL([ContFax], '') + '"'
							FROM	INSERTED
							WHERE	VendorID = @VendorID)

			SET @JsonData = '[{' + @JsonData + '}]'

			EXEC api_sendrequest @Operation, @Url, @JsonData
				
			FETCH NEXT FROM inserted_cursor INTO @VendorID
		END

		CLOSE inserted_cursor
		DEALLOCATE inserted_cursor
	END

	-- Check if rows were updated
	IF EXISTS(SELECT * from INSERTED) AND EXISTS (SELECT * from DELETED)
	BEGIN
		SET @VendorID = (SELECT VendorID FROM INSERTED)
		SET @Operation = 'U'
		PRINT(@Operation)
		
		-- Use a cursor to iterate over deleted rows
		DECLARE updated_cursor CURSOR FOR
			SELECT VendorID FROM INSERTED

		OPEN updated_cursor
		FETCH NEXT FROM updated_cursor INTO @VendorID

		WHILE @@FETCH_STATUS = 0
		BEGIN
			SET @Url = @BaseUrl + 'edit/?dbNum=' + @DbNum  -- Specify INSERT URL

			-- Construct JSON data based on the current row
			SET @JsonData =	(SELECT 
							'"' + 'VendorID' + '":"' + ISNULL(CAST([VendorID] AS NVARCHAR(MAX)), '') + '",' +
							'"' + 'VendorTitle' + '":"' + ISNULL([VendorTitle], '') + '",' +
							'"' + 'VendorName' + '":"' + ISNULL([VendorName], '') + '",' +
							'"' + 'VendorNameEng' + '":"' + ISNULL([VendorNameEng], '') + '",' +
							'"' + 'ShortName' + '":"' + ISNULL([ShortName], '') + '",' +
							'"' + 'VendorCode' + '":"' + ISNULL([VendorCode], '') + '",' +
							'"' + 'VendorType' + '":"' + ISNULL([VendorType], '') + '",' +
							'"' + 'VendorAddr1' + '":"' + ISNULL([VendorAddr1], '') + '",' +
							'"' + 'VendorAddr2' + '":"' + ISNULL([VendorAddr2], '') + '",' +
							'"' + 'District' + '":"' + ISNULL([District], '') + '",' +
							'"' + 'Amphur' + '":"' + ISNULL([Amphur], '') + '",' +
							'"' + 'Province' + '":"' + ISNULL([Province], '') + '",' +
							'"' + 'PostCode' + '":"' + ISNULL([PostCode], '') + '",' +
							'"' + 'TaxId' + '":"' + ISNULL([TaxId], '') + '",' +
							'"' + 'ContTel' + '":"' + ISNULL([ContTel], '') + '",' +
							'"' + 'ContFax' + '":"' + ISNULL([ContFax], '') + '"'
							FROM	INSERTED
							WHERE	VendorID = @VendorID)

			SET @JsonData = '[{' + @JsonData + '}]'

			EXEC api_sendrequest @Operation, @Url, @JsonData

			FETCH NEXT FROM updated_cursor INTO @VendorID
		END

		CLOSE updated_cursor
		DEALLOCATE updated_cursor
	END
END
GO