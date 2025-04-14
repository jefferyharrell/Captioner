from sqlalchemy import Column, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Photo(Base):
    __tablename__ = "photos"
    id = Column(String, primary_key=True, index=True)  # UUID string
    filename = Column(String, nullable=False)
    hash = Column(String, unique=True, nullable=False)
    caption = Column(Text, nullable=True)
