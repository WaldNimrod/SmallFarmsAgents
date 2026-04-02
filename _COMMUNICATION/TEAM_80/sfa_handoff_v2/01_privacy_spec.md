# Privacy & Data Ethics — Product Specification

## Core Principle (Non-negotiable)
The system must NEVER expose identifiable farm-level data.

## Rules

### Forbidden
- Specific farm pricing
- Identifiable records
- Raw submissions
- Any dataset that allows reverse identification

### Allowed
- Aggregated values
- Statistical ranges
- Normalized models

## UI Rules
- Never display single-source values
- Always show ranges when possible
- Avoid low-sample exposure

## Pipeline Rules
- Anonymization BEFORE storage if possible
- Aggregation BEFORE display (mandatory)
- Minimum sample threshold per datapoint

## Messaging (UI snippet)
"המערכת מציגה נתונים מצרפיים בלבד — ללא חשיפת מידע אישי של חוות."
