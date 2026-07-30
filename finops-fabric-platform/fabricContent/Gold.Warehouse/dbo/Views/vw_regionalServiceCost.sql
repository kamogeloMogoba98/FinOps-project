-- Auto Generated (Do not modify) FB2CAFF4DCC2316B5B75006F30190E00A79B97ECC30A80806F53E552F26A06A0
CREATE VIEW dbo.vw_regionalServiceCost AS
SELECT 
    r.provider,
    r.region,
    r.resourceType,
    SUM(f.effectiveCost) AS TotalEffectiveCost,
    SUM(f.billedCost) AS TotalBilledCost
FROM dbo.factCost f
INNER JOIN dbo.dimResource r ON f.resourceKey = r.resourceKey
GROUP BY r.provider, r.region, r.resourceType;