CREATE TABLE [dbo].[dimCostCenter] (

	[costcentercode] varchar(max) NULL, 
	[department] varchar(max) NULL, 
	[businessUnit] varchar(max) NOT NULL, 
	[ownerEmail] varchar(max) NULL, 
	[budgetCode] varchar(max) NULL, 
	[costCenterKey] int NOT NULL
);