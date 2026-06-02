-- G-V1.1 QA T03 — LOD400 §A2.3 — SRC021 unresolvable names (target: <= 10)
SELECT COUNT(DISTINCT rei.raw_product_name) AS src021_unresolvable
FROM raw_extracted_items rei
JOIN source_fetch_runs sfr ON rei.source_fetch_run_id = sfr.id
JOIN sources s ON sfr.source_id = s.id
WHERE s.code = 'SRC021'
  AND rei.extraction_status = 'unresolvable'
  AND rei.is_quarantined = false;
