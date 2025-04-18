from sqlalchemy import Column, String, Text
from typing import Optional
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Photo(Base):
    __tablename__: str = "photos"
    hash: str = Column(String, primary_key=True, nullable=False)
    filename: str = Column(String, nullable=False)
    caption: Optional[str] = Column(Text, nullable=True)
    # Add future metadata fields here as needed
