CREATE TABLE [dbo].[factCost] (

	[dateKey] int NULL, 
	[resourceKey] int NULL, 
	[costCenterKey] int NULL, 
	[tagKey] int NULL, 
	[commitmentKey] int NULL, 
	[chargetype] varchar(max) NULL, 
	[pricingmodel] varchar(max) NULL, 
	[billedCost] float NULL, 
	[effectiveCost] float NULL, 
	[listCost] float NULL, 
	[usageQuantity] float NULL, 
	[usageUnit] varchar(max) NULL, 
	[costFactKey] bigint NOT NULL
);