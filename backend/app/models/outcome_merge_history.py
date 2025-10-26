"""
OutcomeMergeHistory model for tracking learning outcome merge operations
"""
from sqlalchemy import Column, String, DateTime, Numeric, Text, JSON
from datetime import datetime
import uuid

from app.core.database import Base


class OutcomeMergeHistory(Base):
    """Audit trail for learning outcome merge operations"""

    __tablename__ = "outcome_merge_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    merge_group_id = Column(String(36), nullable=False, index=True)  # Groups related merges

    # Merge metadata
    merged_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    merged_by = Column(String(100), default="system")  # For future multi-user support

    # Merge details
    original_outcome_id = Column(String(36), nullable=False, index=True)
    target_outcome_id = Column(String(36), nullable=False, index=True)

    # Store original data for undo capability
    original_data = Column(JSON)  # Full snapshot of original outcome before merge
    target_data_before = Column(JSON)  # Target outcome state before merge

    # Analysis metadata
    confidence_score = Column(Numeric(5, 2))  # Claude's confidence (0-100)
    similarity_reason = Column(Text)  # Why these were grouped

    # Undo tracking
    undone_at = Column(DateTime, nullable=True)
    undone_by = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        status = "UNDONE" if self.undone_at else "ACTIVE"
        return f"<OutcomeMergeHistory(group={self.merge_group_id}, status={status})>"
