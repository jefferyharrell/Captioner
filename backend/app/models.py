from sqlalchemy import Column, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

from sqlalchemy import Column, String, Text, PrimaryKeyConstraint

class Photo(Base):
    __tablename__ = "photos"
    hash = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    caption = Column(Text, nullable=True)
    __table_args__ = (
        PrimaryKeyConstraint('hash', 'filename', name='photo_pk'),
    )
    # Add future metadata fields here as needed
