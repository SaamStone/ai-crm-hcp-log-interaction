from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Integer, String, Text

from .database import Base


class HCP(Base):
    """Master data for Healthcare Professionals a field rep can log interactions with."""

    __tablename__ = "hcps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    specialty = Column(String(255), nullable=True)
    hospital = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)


class Interaction(Base):
    """A logged HCP interaction, saved once the rep confirms the AI-assisted form."""

    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_name = Column(String(255), nullable=True)
    interaction_type = Column(String(100), nullable=True)
    date = Column(String(50), nullable=True)
    time = Column(String(50), nullable=True)
    attendees = Column(Text, nullable=True)
    topics_discussed = Column(Text, nullable=True)
    materials_shared = Column(JSON, nullable=True, default=list)
    samples_distributed = Column(JSON, nullable=True, default=list)
    sentiment = Column(String(50), nullable=True)
    outcomes = Column(Text, nullable=True)
    follow_up_actions = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
