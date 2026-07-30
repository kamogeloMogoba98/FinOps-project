-- Auto Generated (Do not modify) 2D0F61455A77A6C1A07791A1A664E45531230105F24235EDBEC5B69C35B54FDC
CREATE VIEW dbo.vw_EnvironmentCostBreakdown AS
SELECT 
    COALESCE(t.environmentTag, 'Untagged/Unknown') AS Environment,
    SUM(f.billedCost) AS TotalBilledCost,
    SUM(f.effectiveCost) AS TotalEffectiveCost,
    SUM(f.listCost) AS TotalListCost
FROM dbo.factCost f
LEFT JOIN dbo.dimTags t ON f.tagKey = t.tagKey
GROUP BY COALESCE(t.environmentTag, 'Untagged/Unknown');