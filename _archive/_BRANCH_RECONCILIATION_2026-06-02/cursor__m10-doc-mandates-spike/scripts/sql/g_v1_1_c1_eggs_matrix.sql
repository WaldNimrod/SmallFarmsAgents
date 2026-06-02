-- G-V1.1 T08 / Phase C1 — LOD400 §C1.1 — PRD067 eggs source × unit matrix
-- Schema: sources.name (not name_he)
SELECT
  s.code AS source_code,
  s.name AS source_name,
  rei.raw_unit_text,
  mu.code AS resolved_unit,
  COUNT(*) AS obs_count
FROM raw_extracted_items rei
JOIN source_fetch_runs sfr ON rei.source_fetch_run_id = sfr.id
JOIN sources s ON sfr.source_id = s.id
JOIN normalized_observations no2 ON no2.raw_extracted_item_id = rei.id
JOIN products p ON no2.product_id = p.id
LEFT JOIN measurement_units mu ON no2.display_unit_id = mu.id
WHERE p.code = 'PRD067'
  AND rei.is_quarantined = false
GROUP BY s.code, s.name, rei.raw_unit_text, mu.code
ORDER BY s.code, obs_count DESC;
