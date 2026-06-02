-- G-V1.1 QA T07 — LOD400 §A1.3 CQ-P09 — inactive basket codes + CSA basket targets

-- Query 4: MUST return 0 rows — no active aliases on PRD028/PRD029
SELECT pa.id, pa.alias_text, p.code AS target_code
FROM product_aliases pa
JOIN products p ON pa.product_id = p.id
WHERE p.code IN ('PRD028', 'PRD029')
  AND pa.is_active = true;

-- Query 5: PRD028/PRD029 must be inactive
SELECT code, canonical_name_he, is_active
FROM products
WHERE code IN ('PRD028', 'PRD029');

-- Query 6: MUST return 0 — no observations on inactive basket codes
SELECT COUNT(*) AS orphan_count
FROM normalized_observations no2
JOIN products p ON no2.product_id = p.id
WHERE p.code IN ('PRD028', 'PRD029');

-- Query 7: CSA basket-style aliases should target PRD025/026/027 only
SELECT pa.alias_text, p.code AS target_code
FROM product_aliases pa
JOIN products p ON pa.product_id = p.id
WHERE (
  pa.alias_text_normalized LIKE '%סל%'
  OR pa.alias_text_normalized LIKE '%ארגז%'
  OR pa.alias_text_normalized LIKE '%basket%'
)
AND pa.is_active = true
ORDER BY p.code;
