"""crop_book.canon — executable representation of the Crop Data Model Canon v1.2.0.

Modules:
    units        — UNIT_REGISTRY + UNIT_VARIANT_MAP + normalize_unit()
    enums        — ENUM_TOKENS + ENUM_COLLAPSE + canonicalize_enum()
    field_registry — FIELD_REGISTRY: field→{canonical, type, unit, layer, disposition}
    derive       — computed accessors (T4 fields — never stored)
    migrate      — CLI runner (per-phase subcommands + --dry-run)
"""
