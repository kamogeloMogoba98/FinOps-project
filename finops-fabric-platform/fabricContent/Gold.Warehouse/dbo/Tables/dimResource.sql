CREATE TABLE [dbo].[dimResource] (

	[resourceid] varchar(max) NULL, 
	[resourcename] varchar(max) NULL, 
	[resourceType] varchar(max) NULL, 
	[region] varchar(max) NULL, 
	[provider] varchar(max) NULL, 
	[resourceKey] int NOT NULL
);