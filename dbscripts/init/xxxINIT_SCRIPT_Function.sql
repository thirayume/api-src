USE [dbwins_demo]
GO

CREATE FUNCTION dbo.SplitString
(
    @string NVARCHAR(MAX),
    @delimiter CHAR(1)
)
RETURNS @output TABLE (Item NVARCHAR(MAX))
AS
BEGIN
    DECLARE @start INT, @end INT;
    
    SET @start = 1;

    WHILE CHARINDEX(@delimiter, @string, @start) > 0
    BEGIN
        SET @end = CHARINDEX(@delimiter, @string, @start);
        INSERT INTO @output (Item)
        VALUES(LTRIM(RTRIM(SUBSTRING(@string, @start, @end - @start))));
        SET @start = @end + 1;
    END

    -- Handle the last item
    INSERT INTO @output (Item)
    VALUES(LTRIM(RTRIM(SUBSTRING(@string, @start, LEN(@string) - @start + 1))));
    
    RETURN;
END
GO

CREATE FUNCTION dbo.RemoveNonPrintableChars
(
    @input NVARCHAR(MAX)
)
RETURNS NVARCHAR(MAX)
AS
BEGIN
    DECLARE @output NVARCHAR(MAX);
    SET @output = @input;

    -- Replace common non-printable characters
    SET @output = REPLACE(@output, CHAR(9), ''); -- Tab
    SET @output = REPLACE(@output, CHAR(10), ''); -- Line Feed
    SET @output = REPLACE(@output, CHAR(13), ''); -- Carriage Return

    -- Trim any remaining spaces
    SET @output = LTRIM(RTRIM(@output));

    RETURN @output;
END
GO