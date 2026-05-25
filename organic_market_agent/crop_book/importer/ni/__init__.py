"""NI importer subclasses (SFA-S003-P002-WP-B2 v1.1.3).

Importing this package re-exports the 6 concrete subclasses.

IMPORTANT — B2 does NOT use `ni_registry.load_all()`. Reason: WP-A's
`NIImporter.validate()` drops rows missing `variety_id`. B2 subclasses
need DB session access to resolve `crop_jmf_en` -> `variety_id`, but
that WP-A registration pattern (which B2 does NOT use) instantiates subclasses at
module-load time with no session available. Therefore:

  - B2 subclasses are NOT registered with ni_registry — the
    `ni_registry.register()` call is NEVER invoked at module load.
  - seed.py iterates `NI_IMPORTER_CLASSES` directly with an open session.
  - Each subclass's `load(self, session)` and
    `load_knowledge_notes(self, session)` accept the session and return
    rows with `variety_id` / `crop_id` already resolved.
  - Rows then flow through `_upsert_source_value(session, variety_id, sv)`
    (existing WP-A helper) and `_upsert_knowledge_note(session, ...)`
    (new helper appended to ni_importer.py per §7.3) — both expect
    fully-resolved keys.

Future generic NI sources whose `load()` does NOT need DB access MAY
still use the `ni_registry.register()` + `load_all()` pattern; B2 simply
takes a different path because of its specific data-shape requirements.
This deviation is acknowledged in spec §7 and AC-15.

This file does NOT call `ni_registry.register()` at module load.
"""
from organic_market_agent.crop_book.importer.ni.jmf_book import JmfBookImporter
from organic_market_agent.crop_book.importer.ni.jmf_book_alt import JmfBookAltImporter
from organic_market_agent.crop_book.importer.ni.jmf_ft_flameweed import JmfFtFlameweedImporter
from organic_market_agent.crop_book.importer.ni.jmf_ft_biopesticide import JmfFtBiopesticideImporter
from organic_market_agent.crop_book.importer.ni.jmf_ft_phytoprotection import JmfFtPhytoprotectionImporter
from organic_market_agent.crop_book.importer.ni.jmf_ft_nurseryseeding import JmfFtNurseryseedingImporter

NI_IMPORTER_CLASSES = (
    JmfBookImporter,
    JmfBookAltImporter,
    JmfFtFlameweedImporter,
    JmfFtBiopesticideImporter,
    JmfFtPhytoprotectionImporter,
    JmfFtNurseryseedingImporter,
)

__all__ = [cls.__name__ for cls in NI_IMPORTER_CLASSES] + ["NI_IMPORTER_CLASSES"]
