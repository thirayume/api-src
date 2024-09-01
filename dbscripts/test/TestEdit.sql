USE [dbwins_demo]
GO

SELECT CHANGE_TRACKING_CURRENT_VERSION(); 
GO

--- STEP: 1 ---
DECLARE @Context varbinary(128) = CAST('1st Update - EMVendor - Modified-VendorName' AS varbinary(128));
WITH CHANGE_TRACKING_CONTEXT (@Context)  
	UPDATE	[dbo].[EMVendor]
	SET		[VendorName] = '11111' 
	WHERE	[VendorID] = 3030
GO
 
SELECT CHANGE_TRACKING_CURRENT_VERSION(); 
GO

--- STEP: 2 ---
DECLARE @Context varbinary(128) = CAST('2nd Update - EMVendor - Modified-ShortName' AS varbinary(128));
WITH CHANGE_TRACKING_CONTEXT (@Context)  
	UPDATE	[dbo].[EMVendor]
	SET		[ShortName] = '11111' 
	WHERE	[VendorID] = 3030

	UPDATE [dbo].[EMGood]
	SET		[GoodName1] = '11111'
	WHERE	[GoodCode] = '11111'
GO
 
SELECT CHANGE_TRACKING_CURRENT_VERSION(); 
GO

--- STEP: 3 ---
DECLARE @Context varbinary(128) = CAST('3rd Update - EMVendor - Modified-VendorName&ShortName' AS varbinary(128));
WITH CHANGE_TRACKING_CONTEXT (@Context)  
	UPDATE	[dbo].[EMVendor]
	SET		[VendorName] = '111'
			,[ShortName] = '111'
			,[TaxId] = '111'
	WHERE	[VendorID] = 3333

	UPDATE [dbo].[EMGood]
	SET		[GoodName1] = '111'
	WHERE	[GoodCode] = '111'
GO
 
SELECT CHANGE_TRACKING_CURRENT_VERSION(); 
GO