CREATE TABLE [dbo].[dimCommitmentDiscount] (

	[CommitmentId] varchar(max) NULL, 
	[CommitmentType] varchar(max) NULL, 
	[term] varchar(max) NULL, 
	[PaymentOption] varchar(max) NOT NULL, 
	[ExpirationDate] date NULL, 
	[CommitmentKey] int NOT NULL
);