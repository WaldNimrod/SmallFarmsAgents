-- G-V1.1 T09 / Phase C2 — LOD400 §C2.1 — PRD072 passion fruit audit
-- Schema: sources.name AS source_name (not name_he)
SELECT
  s.code AS source_code,
  s.name AS source_name,
  rei.raw_unit_text,
  rei.raw_price_text,
  no2.normalized_price_value,
  mu.code AS resolved_unit
FROM raw_extracted_items rei
JOIN source_fetch_runs sfr ON rei.source_fetch_run_id = sfr.id
JOIN sources s ON sfr.source_id = s.id
JOIN normalized_observations no2 ON no2.raw_extracted_item_id = rei.id
JOIN products p ON no2.product_id = p.id
LEFT JOIN measurement_units mu ON no2.display_unit_id = mu.id
WHERE p.code = 'PRD072'
  AND rei.is_quarantined = false
ORDER BY s.code, no2.observed_at DESC;
