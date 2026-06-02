-- G-V1.1 QA T02 — LOD400 §A2.3 — distinct unresolvable product names (target: <= 20)
SELECT COUNT(DISTINCT raw_product_name) AS distinct_unresolvable
FROM raw_extracted_items
WHERE extraction_status = 'unresolvable' AND is_quarantined = false;
