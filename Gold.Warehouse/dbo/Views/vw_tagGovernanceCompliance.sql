-- Auto Generated (Do not modify) 8D3395A4F159AF70F06627558FF41C494EE152FB232BA27E8609CC6A8C6D6B90
CREATE VIEW dbo.vw_tagGovernanceCompliance AS
SELECT 
    SUM(CASE WHEN t.applicationTag IS NULL OR t.costOwnerTag IS NULL THEN f.effectiveCost ELSE 0 END) AS UnallocatedEffectiveCost,
    SUM(f.effectiveCost) AS TotalEffectiveCost,
    (SUM(CASE WHEN t.applicationTag IS NULL OR t.costOwnerTag IS NULL THEN f.effectiveCost ELSE 0 END) * 100.0) / NULLIF(SUM(f.effectiveCost), 0) AS UnallocatedPercentage
FROM dbo.factCost f
LEFT JOIN dbo.dimTags t ON f.tagKey = t.tagKey;