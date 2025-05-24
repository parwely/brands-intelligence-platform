# backend/app/models/brand.py
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
from ..core.database import Base
import uuid

class Brand(Base):
    __tablename__ = "brands"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))  # String instead of UUID
    name = Column(String, nullable=False)
    industry = Column(String)
    website = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())