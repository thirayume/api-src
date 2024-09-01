USE [dbwins_demo]
GO

INSERT INTO [dbo].[EMVendor]
           (
            [VendorID]
           ,[VendorTitle]
           ,[VendorName]
           ,[VendorNameEng]
           ,[ShortName]
           ,[VendorCode]
           ,[VendorType]
           ,[VendorAddr1]
           ,[VendorAddr2]
           ,[District]
           ,[Amphur]
           ,[Province]
           ,[PostCode]
           ,[TaxId]
           ,[ContTel]
		   ,[ContFax]
		   )
     VALUES
           (
				  3333,
				  '����ѷ',
				  '�ͺի� �ӡѴ',
				  'ABC',
				  'ABC',
				  '�-3030',
				  '1',
				  '252 �.�Ҵ�����',
				  null,
				  '�ǧ�ѧ�ͧ��ҧ',
				  'ࢵ�ѧ�ͧ��ҧ',
				  '��ا෾',
				  '10250',
				  '0001112223334',
				  '0-2733-2522',
				  '0-2733-2523'
		   )
GO


