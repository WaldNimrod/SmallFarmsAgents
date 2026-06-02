-- G-V1.1 QA T11 — LOD400 §C4.5 — basket tier distribution after catalog_renormalize
-- Run after: python -m organic_market_agent catalog_renormalize
SELECT p.code, p.canonical_name_he, COUNT(*) AS obs_count
FROM normalized_observations no2
JOIN products p ON no2.product_id = p.id
WHERE p.category = 'baskets' AND p.is_active = true
GROUP BY p.code, p.canonical_name_he
ORDER BY p.code;
