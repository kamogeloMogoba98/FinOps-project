CREATE PROCEDURE dbo.GetExecutiveCostSummary
AS
BEGIN
    -- 1. Environment Summary
    SELECT 'Environment Breakdown' AS MetricType, Environment AS Category, TotalEffectiveCost 
    FROM dbo.vw_EnvironmentCostBreakdown;

    -- 2. Governance Summary
    SELECT 'Tag Governance' AS MetricType, 'Unallocated Percentage' AS Category, UnallocatedPercentage AS TotalEffectiveCost 
    FROM dbo.vw_tagGovernanceCompliance;

    -- 3. Top Cost Drivers (Top 5 Services/Regions)
    SELECT TOP 5 'Top Cost Driver' AS MetricType, CONCAT(provider, ' - ', region, ' - ', resourceType) AS Category, TotalEffectiveCost 
    FROM dbo.vw_regionalServiceCost
    ORDER BY TotalEffectiveCost DESC;
END;