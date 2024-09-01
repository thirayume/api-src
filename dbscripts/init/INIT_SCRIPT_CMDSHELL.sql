USE [dbwins_demo]
GO

sp_configure 'show advanced options', 1;
RECONFIGURE
GO

sp_configure 'xp_cmdshell', 1;
RECONFIGURE
GO