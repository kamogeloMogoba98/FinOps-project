CREATE TABLE [dbo].[dimDate] (

	[fullDate] date NULL, 
	[date_key] int NULL, 
	[dayOfWeek] varchar(max) NULL, 
	[monthName] varchar(max) NULL, 
	[quarter] int NULL, 
	[fiscalYear] int NULL, 
	[billingMonth] int NULL
);