"""Junction Table ORM — crop_knowledge_notes ↔ crops (many-to-many).

SFA-S003-P002-WP-B1-patch04 LOD400 §3.4.
Implements the many-to-many link introduced by Migration 047.
Cross-crop notes (e.g., storage/washing sheet 056) can reference multiple crops.
"""
from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, Table

from organic_market_agent.db.base import Base

# Association table — SQLAlchemy Table() object (not a full ORM model class).
# Used as `secondary=` in the CropKnowledgeNote.crops_linked relationship.
crop_knowledge_notes_crops = Table(
    'crop_knowledge_notes_crops',
    Base.metadata,
    Column(
        'note_id',
        Integer,
        ForeignKey('crop_knowledge_notes.id', ondelete='CASCADE'),
        primary_key=True,
        nullable=False,
    ),
    Column(
        'crop_id',
        Integer,
        ForeignKey('crops.id', ondelete='CASCADE'),
        primary_key=True,
        nullable=False,
    ),
)
