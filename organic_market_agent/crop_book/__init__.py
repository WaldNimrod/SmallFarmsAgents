# patch04: ensure junction table and its FK target are registered in Base.metadata
# on any import of the crop_book package.
from organic_market_agent.crop_book.crop_knowledge_notes import CropKnowledgeNote  # noqa: F401
from organic_market_agent.crop_book.crop_knowledge_notes_crops import (  # noqa: F401
    crop_knowledge_notes_crops,
)
