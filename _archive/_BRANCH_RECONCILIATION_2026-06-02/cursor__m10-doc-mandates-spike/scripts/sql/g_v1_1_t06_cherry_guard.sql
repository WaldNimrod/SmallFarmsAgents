-- G-V1.1 QA T06 — LOD400 §A1.2 CQ-P08 — cherry guard (three queries)

-- Query 1: MUST return 0 rows — no cherry-token aliases on PRD001
SELECT pa.id, pa.alias_text, pa.alias_text_normalized, p.code
FROM product_aliases pa
JOIN products p ON pa.product_id = p.id
WHERE p.code = 'PRD001'
  AND pa.is_active = true
  AND (
    pa.alias_text_normalized LIKE '%שרי%'
    OR pa.alias_text_normalized LIKE '%cherry%'
    OR pa.alias_text_normalized LIKE '%צ''רי%'
  );

-- Query 2: MUST return >= 1 row — cherry aliases on PRD002
SELECT pa.id, pa.alias_text, p.code
FROM product_aliases pa
JOIN products p ON pa.product_id = p.id
WHERE p.code = 'PRD002'
  AND pa.is_active = true
  AND (
    pa.alias_text_normalized LIKE '%שרי%'
    OR pa.alias_text_normalized LIKE '%cherry%'
  );

-- Query 3: MUST return 0 rows — no cherry observations on PRD001
SELECT rei.raw_product_name, no2.product_id, p.code
FROM normalized_observations no2
JOIN products p ON no2.product_id = p.id
JOIN raw_extracted_items rei ON no2.raw_extracted_item_id = rei.id
WHERE p.code = 'PRD001'
  AND (
    rei.raw_product_name LIKE '%שרי%'
    OR rei.raw_product_name LIKE '%cherry%'
  );
