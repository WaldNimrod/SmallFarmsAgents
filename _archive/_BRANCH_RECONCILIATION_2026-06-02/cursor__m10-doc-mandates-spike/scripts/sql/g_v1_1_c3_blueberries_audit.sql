-- G-V1.1 T10 / Phase C3 — LOD400 §C3.1 — PRD086 blueberries audit
-- Schema: sources.name AS source_name (not name_he)
SELECT
  s.code AS source_code,
  s.name AS source_name,
  rei.raw_product_name,
  rei.raw_unit_text,
  no2.normalized_price_value,
  mu.code AS unit
FROM raw_extracted_items rei
JOIN source_fetch_runs sfr ON rei.source_fetch_run_id = sfr.id
JOIN sources s ON sfr.source_id = s.id
JOIN normalized_observations no2 ON no2.raw_extracted_item_id = rei.id
JOIN products p ON no2.product_id = p.id
LEFT JOIN measurement_units mu ON no2.display_unit_id = mu.id
WHERE p.code = 'PRD086'
  AND rei.is_quarantined = false
ORDER BY s.code;
