#!/usr/bin/env python3
"""
Ingest SFA hub feedback export JSON into hub/ssot/responses/
and update hub/ssot/manifest.json.

Usage (repo root):
  python3 scripts/ingest_sfa_feedback_json.py path/to/export.json --by "Name"
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import date
from pathlib import Path

EXPECTED_EXPORT_TYPE = "sfa-feedback"


def root_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def load_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> None:
    ap = argparse.ArgumentParser(description="Ingest SFA hub feedback JSON")
    ap.add_argument("export_file", type=Path, help="Path to sfa-feedback-*.json from browser export")
    ap.add_argument("--by", default="team", help="Recorder name for manifest")
    args = ap.parse_args()

    root = root_dir()
    decisions_path = root / "hub" / "data" / "decisions.json"
    ssot_dir = root / "hub" / "ssot"
    responses_dir = ssot_dir / "responses"
    manifest_path = ssot_dir / "manifest.json"

    decisions_data = load_json(decisions_path)
    valid_ids = {d["id"] for d in decisions_data.get("decisions", []) if d.get("id")}

    raw = args.export_file.read_text(encoding="utf-8")
    data = json.loads(raw)

    if data.get("schemaVersion") != 1:
        raise SystemExit("Unsupported schemaVersion (expected 1)")
    if data.get("exportType") != EXPECTED_EXPORT_TYPE:
        raise SystemExit(f"Unsupported exportType (expected {EXPECTED_EXPORT_TYPE})")
    if not data.get("exportTimestamp"):
        raise SystemExit("Missing exportTimestamp")

    answers = data.get("answers") or []
    if not answers:
        raise SystemExit("No answers in export (nothing to ingest)")
    for a in answers:
        qid = a.get("id")
        if not qid or qid not in valid_ids:
            raise SystemExit(f"Unknown or missing decision id: {qid!r}")
        if not (str(a.get("choice", "")).strip() or str(a.get("notes", "")).strip()):
            raise SystemExit(f"Empty answer for {qid}")

    responses_dir.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:10]
    d = date.today().isoformat()
    slug = re.sub(r"[^\w\-]+", "-", args.by.strip())[:24] or "team"
    out_name = f"{d}--sfa-feedback--{slug}--{h}.json"
    out_path = responses_dir / out_name
    if out_path.exists():
        raise SystemExit(f"Refusing overwrite: {out_path}")

    payload = {
        "schemaVersion": 1,
        "ingestType": "sfa-feedback",
        "ingestedAt": d,
        "ingestedBy": args.by,
        "sourceExport": data,
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    man = load_json(manifest_path) if manifest_path.is_file() else {"schemaVersion": 1, "ingestedExports": []}
    man.setdefault("ingestedExports", []).append(
        {"file": f"responses/{out_name}", "ingestedBy": args.by, "exportTimestamp": data["exportTimestamp"]}
    )
    man["lastIngestIso"] = data["exportTimestamp"]
    manifest_path.write_text(json.dumps(man, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"OK: wrote {out_path}", flush=True)


if __name__ == "__main__":
    main()
